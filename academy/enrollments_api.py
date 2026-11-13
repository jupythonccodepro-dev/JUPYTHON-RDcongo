from django.db import models, transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import (
    CourseLesson,
    CourseModule,
    Enrollment,
    Formation,
    LessonProgress,
    LessonPracticeSubmission,
    ModuleQuizProgress,
)


QUIZ_PASSING_PERCENT = 67


def _module_is_unlocked(user, module):
    previous_modules = CourseModule.objects.filter(formation=module.formation).filter(
        models.Q(order__lt=module.order) | models.Q(order=module.order, id__lt=module.id)
    )
    for previous in previous_modules:
        lesson_ids = list(previous.lessons.values_list('id', flat=True))
        if not lesson_ids or LessonProgress.objects.filter(user=user, lesson_id__in=lesson_ids).count() != len(lesson_ids):
            return False
        if not ModuleQuizProgress.objects.filter(user=user, module=previous, passed=True).exists():
            return False
    return True


def _passed_module_ids(user, formation):
    return list(
        ModuleQuizProgress.objects.filter(
            user=user,
            module__formation=formation,
            passed=True,
        ).values_list('module_id', flat=True)
    )


class EnrollAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        formation_id = request.data.get('formation_id') or request.data.get('formation')
        if not formation_id:
            return Response({'error': 'formation_id manquant'}, status=400)

        try:
            formation = Formation.objects.get(id=int(formation_id))
        except (Formation.DoesNotExist, ValueError, TypeError):
            return Response({'error': 'Formation non trouvée'}, status=404)

        enrollment, created = Enrollment.objects.get_or_create(user=request.user, formation=formation)
        return Response({
            'enrolled': created,
            'already_enrolled': not created,
            'formation_id': formation.id,
        })


class MyEnrollmentsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        enrollments = Enrollment.objects.filter(user=request.user).select_related('formation').prefetch_related(
            'formation__modules__lessons',
            'formation__modules__quiz_questions',
        )
        completed_lesson_ids = set(
            LessonProgress.objects.filter(
                user=request.user,
                lesson__module__formation__in=[enrollment.formation for enrollment in enrollments],
            ).values_list('lesson_id', flat=True)
        )
        data = [
            {
                'id': e.id,
                'formation': {
                    'id': e.formation.id,
                    'title': e.formation.title,
                    'platform': e.formation.platform,
                    'link': e.formation.link,
                    'hosted_by_jupython': e.formation.hosted_by_jupython,
                    'cover_image': request.build_absolute_uri(e.formation.cover_image.url) if e.formation.cover_image else '',
                    'cover_image_url': e.formation.cover_image_url,
                    'provider_logo_url': e.formation.provider_logo_url,
                },
                'date_joined': e.date_joined,
                'status': e.status,
                'progress': self._course_progress(e.formation, completed_lesson_ids, request.user),
            }
            for e in enrollments
        ]
        return Response(data)

    @staticmethod
    def _course_progress(formation, completed_lesson_ids, user):
        lesson_ids = [
            lesson.id
            for module in formation.modules.all()
            for lesson in module.lessons.all()
        ]
        completed_ids = [lesson_id for lesson_id in lesson_ids if lesson_id in completed_lesson_ids]
        completed = len(completed_ids)
        total = len(lesson_ids)
        quiz_module_ids = [
            module.id
            for module in formation.modules.all()
            if module.quiz_questions.exists()
        ]
        passed_module_ids = _passed_module_ids(user, formation)
        practice_submissions = {
            submission.lesson_id: {
                'status': submission.status,
                'feedback': submission.feedback,
            }
            for submission in LessonPracticeSubmission.objects.filter(
                user=user, lesson__module__formation=formation
            )
        }
        completed_quizzes = sum(module_id in passed_module_ids for module_id in quiz_module_ids)
        total_units = total + len(quiz_module_ids)
        return {
            'has_curriculum': formation.hosted_by_jupython and total > 0,
            'completed_lessons': completed,
            'completed_lesson_ids': completed_ids,
            'practice_submissions': practice_submissions,
            'completed_quizzes': completed_quizzes,
            'total_quizzes': len(quiz_module_ids),
            'passed_module_ids': passed_module_ids,
            'total_lessons': total,
            'percent': round((completed + completed_quizzes) * 100 / total_units) if total_units else 0,
        }


class EnrollmentProgressAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, enrollment_id):
        try:
            enrollment = Enrollment.objects.get(id=enrollment_id, user=request.user)
        except Enrollment.DoesNotExist:
            return Response({'error': 'Inscription non trouvée'}, status=404)

        if enrollment.formation.hosted_by_jupython:
            return Response(
                {'error': 'La progression de ce parcours est calculée à partir des leçons terminées'},
                status=400,
            )

        status_value = request.data.get('status')
        valid_statuses = {choice[0] for choice in Enrollment.STATUS_CHOICES}
        if not isinstance(status_value, str) or status_value not in valid_statuses:
            return Response(
                {'error': 'Statut invalide'},
                status=400,
            )

        enrollment.status = status_value
        enrollment.save(update_fields=['status'])
        return Response({'id': enrollment.id, 'status': enrollment.status})


class LessonPracticeSubmissionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, lesson_id):
        try:
            lesson = CourseLesson.objects.select_related('module__formation').get(id=lesson_id)
        except CourseLesson.DoesNotExist:
            return Response({'error': 'Le?on non trouv?e'}, status=404)

        formation = lesson.module.formation
        if not formation.hosted_by_jupython:
            return Response({'error': 'Cette le?on ne fait pas partie d?un cours Jupython'}, status=400)
        if not lesson.exercise.strip():
            return Response({'error': 'Cette le?on ne contient pas encore d?exercice ? soumettre.'}, status=400)
        if not Enrollment.objects.filter(user=request.user, formation=formation).exists():
            return Response({'error': 'Inscrivez-vous ? ce cours avant de soumettre un exercice.'}, status=403)
        if not _module_is_unlocked(request.user, lesson.module):
            return Response({'error': 'R?ussissez le test du module pr?c?dent pour continuer.'}, status=403)

        response_text = request.data.get('response', '')
        if not isinstance(response_text, str) or len(response_text.strip()) < 30:
            return Response({'error': 'D?cris ton travail en au moins 30 caract?res, ou colle un lien vers ton projet.'}, status=400)
        if len(response_text) > 20000:
            return Response({'error': 'La r?ponse ne peut pas d?passer 20 000 caract?res.'}, status=400)

        existing = LessonPracticeSubmission.objects.filter(user=request.user, lesson=lesson).first()
        if existing and existing.status == LessonPracticeSubmission.STATUS_APPROVED:
            return Response({'error': 'Cet exercice est d?j? valid?.'}, status=400)
        submission, _ = LessonPracticeSubmission.objects.update_or_create(
            user=request.user,
            lesson=lesson,
            defaults={
                'response': response_text.strip(),
                'status': LessonPracticeSubmission.STATUS_PENDING,
                'feedback': '',
                'reviewed_at': None,
                'reviewer': None,
            },
        )
        return Response({
            'lesson_id': lesson.id,
            'submission_status': submission.status,
            'message': 'Travail envoy?. La progression sera valid?e apr?s correction par l??quipe.',
        }, status=201)


class LessonProgressAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, lesson_id):
        try:
            lesson = CourseLesson.objects.select_related('module__formation').get(id=lesson_id)
        except CourseLesson.DoesNotExist:
            return Response({'error': 'Leçon non trouvée'}, status=404)

        formation = lesson.module.formation
        if not formation.hosted_by_jupython:
            return Response({'error': 'Cette leçon ne fait pas partie d’un cours Jupython'}, status=400)
        if not Enrollment.objects.filter(user=request.user, formation=formation).exists():
            return Response({'error': 'Inscrivez-vous à ce cours avant de suivre les leçons'}, status=403)
        if not _module_is_unlocked(request.user, lesson.module):
            return Response({'error': 'Réussissez le test du module précédent pour continuer'}, status=403)

        submission = LessonPracticeSubmission.objects.filter(
            user=request.user, lesson=lesson, status=LessonPracticeSubmission.STATUS_APPROVED
        ).first()
        if submission is None:
            return Response(
                {'error': 'Soumettez votre exercice. La le?on sera valid?e apr?s correction par l??quipe.'},
                status=409,
            )
        LessonProgress.objects.get_or_create(user=request.user, lesson=lesson)
        progress = self._update_enrollment_status(request.user, formation)
        return Response({'lesson_id': lesson.id, 'completed': True, **progress})

    def delete(self, request, lesson_id):
        try:
            lesson = CourseLesson.objects.select_related('module__formation').get(id=lesson_id)
        except CourseLesson.DoesNotExist:
            return Response({'error': 'Leçon non trouvée'}, status=404)

        formation = lesson.module.formation
        if not formation.hosted_by_jupython:
            return Response({'error': 'Cette leçon ne fait pas partie d’un cours Jupython'}, status=400)
        enrollment = Enrollment.objects.filter(user=request.user, formation=formation).first()
        if enrollment is None:
            return Response({'error': 'Inscription non trouvée'}, status=403)
        if not _module_is_unlocked(request.user, lesson.module):
            return Response({'error': 'Ce module est encore verrouillé'}, status=403)

        LessonProgress.objects.filter(user=request.user, lesson=lesson).delete()
        progress = self._update_enrollment_status(request.user, formation)
        return Response({'lesson_id': lesson.id, 'completed': False, **progress})

    @staticmethod
    def _update_enrollment_status(user, formation):
        lessons = CourseLesson.objects.filter(module__formation=formation)
        total = lessons.count()
        completed = LessonProgress.objects.filter(user=user, lesson__module__formation=formation).count()
        enrollment = Enrollment.objects.get(user=user, formation=formation)
        quiz_modules = CourseModule.objects.filter(
            formation=formation,
            quiz_questions__isnull=False,
        ).distinct()
        passed_quizzes = ModuleQuizProgress.objects.filter(
            user=user,
            module__in=quiz_modules,
            passed=True,
        ).count()
        all_quizzes_passed = not quiz_modules.exists() or passed_quizzes == quiz_modules.count()
        total_quizzes = quiz_modules.count()
        progress_percent = round(
            (completed + passed_quizzes) * 100 / (total + total_quizzes)
        ) if total + total_quizzes else 0
        enrollment.status = (
            Enrollment.STATUS_COMPLETED if total and completed == total and all_quizzes_passed
            else Enrollment.STATUS_IN_PROGRESS if completed
            else Enrollment.STATUS_ENROLLED
        )
        enrollment.save(update_fields=['status'])
        return {
            'status': enrollment.status,
            'completed_lessons': completed,
            'total_lessons': total,
            'completed_quizzes': passed_quizzes,
            'total_quizzes': total_quizzes,
            'percent': progress_percent,
        }


class ModuleQuizAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, module_id):
        module, error_response = self._get_accessible_module(request.user, module_id)
        if error_response:
            return error_response

        progress = ModuleQuizProgress.objects.filter(user=request.user, module=module).first()
        return Response({
            'module_id': module.id,
            'questions': [
                {
                    'id': question.id,
                    'prompt': question.prompt,
                    'choices': question.choices,
                    'order': question.order,
                }
                for question in module.quiz_questions.all()
            ],
            'passed': progress.passed if progress else False,
            'best_score': progress.best_score if progress else 0,
            'attempts': progress.attempts if progress else 0,
            'passing_score': QUIZ_PASSING_PERCENT,
        })

    def post(self, request, module_id):
        module, error_response = self._get_accessible_module(request.user, module_id)
        if error_response:
            return error_response

        questions = list(module.quiz_questions.all())
        answers = request.data.get('answers')
        question_ids = {str(question.id) for question in questions}
        if not isinstance(answers, dict) or set(answers) != question_ids:
            return Response({'error': 'Réponds à toutes les questions du test'}, status=400)
        if any(
            isinstance(answers[str(question.id)], bool)
            or not isinstance(answers[str(question.id)], int)
            or answers[str(question.id)] < 0
            or answers[str(question.id)] >= len(question.choices)
            for question in questions
        ):
            return Response({'error': 'Une ou plusieurs réponses sont invalides'}, status=400)

        correct = sum(
            answers[str(question.id)] == question.correct_choice
            for question in questions
        )
        score = round(correct * 100 / len(questions))
        passed_attempt = correct * 3 >= len(questions) * 2
        with transaction.atomic():
            progress, _ = ModuleQuizProgress.objects.get_or_create(
                user=request.user,
                module=module,
            )
            progress = ModuleQuizProgress.objects.select_for_update().get(pk=progress.pk)
            progress.attempts += 1
            progress.best_score = max(progress.best_score, score)
            progress.passed = progress.passed or passed_attempt
            progress.save(update_fields=['attempts', 'best_score', 'passed', 'updated_at'])

        status = LessonProgressAPIView._update_enrollment_status(request.user, module.formation)['status']
        return Response({
            'module_id': module.id,
            'score': score,
            'best_score': progress.best_score,
            'passed': progress.passed,
            'attempts': progress.attempts,
            'passed_module_ids': _passed_module_ids(request.user, module.formation),
            'status': status,
            'passing_score': QUIZ_PASSING_PERCENT,
        })

    @staticmethod
    def _get_accessible_module(user, module_id):
        try:
            module = CourseModule.objects.prefetch_related('quiz_questions', 'lessons').get(id=module_id)
        except CourseModule.DoesNotExist:
            return None, Response({'error': 'Module non trouvé'}, status=404)

        if not module.formation.hosted_by_jupython:
            return None, Response({'error': 'Ce module ne fait pas partie d’un parcours Jupython'}, status=400)
        if not Enrollment.objects.filter(user=user, formation=module.formation).exists():
            return None, Response({'error': 'Inscris-toi au parcours pour accéder au test'}, status=403)
        if not _module_is_unlocked(user, module):
            return None, Response({'error': 'Réussis le test du module précédent pour continuer'}, status=403)
        lesson_ids = list(module.lessons.values_list('id', flat=True))
        if not lesson_ids or LessonProgress.objects.filter(user=user, lesson_id__in=lesson_ids).count() != len(lesson_ids):
            return None, Response({'error': 'Termine toutes les leçons du module avant le test'}, status=409)
        if not module.quiz_questions.exists():
            return None, Response({'error': 'Le test de ce module n’est pas encore disponible'}, status=409)
        return module, None
