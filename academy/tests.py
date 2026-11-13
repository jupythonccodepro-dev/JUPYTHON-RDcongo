from io import BytesIO
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image
from rest_framework.test import APITestCase

from accounts.models import User
from academy.models import (
    Certificate,
    CourseLesson,
    CourseModule,
    Enrollment,
    Formation,
    LessonProgress,
    LessonPracticeSubmission,
    ModuleQuizProgress,
    ModuleQuizQuestion,
)


class AcademyBusinessRulesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='StrongPass123',
            university='UPN',
        )
        self.formation = Formation.objects.create(
            title='Python Basics',
            platform='Coursera',
            link='https://example.com/python',
            is_free=True,
        )

    def test_user_can_enroll_only_once_per_formation(self):
        Enrollment.objects.create(user=self.user, formation=self.formation)

        duplicate = Enrollment.objects.filter(user=self.user, formation=self.formation).count()
        self.assertEqual(duplicate, 1)

    def test_formation_store_has_expected_fields(self):
        self.assertTrue(self.formation.title)
        self.assertTrue(self.formation.link)


class CourseCatalogTests(APITestCase):
    def test_curated_provider_courses_are_available_after_migration(self):
        self.assertGreaterEqual(Formation.objects.count(), 10)

        python_course = Formation.objects.get(title='Python Essentials 1')
        self.assertEqual(python_course.platform, 'Cisco Networking Academy')
        self.assertIn('PCEP', python_course.credential_info)
        self.assertIn('Bases de Python', python_course.skills)

    def test_public_catalog_api_returns_course_details(self):
        response = self.client.get('/api/formations/')

        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data), 10)
        python_course = next(course for course in response.data if course['title'] == 'Python Essentials 1')
        self.assertEqual(python_course['language'], 'Français')
        self.assertIn('Bases de Python', python_course['skills'])

    def test_jupython_tracks_have_in_site_lessons(self):
        paths = Formation.objects.filter(hosted_by_jupython=True)

        self.assertEqual(paths.count(), 7)
        self.assertEqual(CourseModule.objects.filter(formation__in=paths).count(), 19)
        self.assertEqual(CourseLesson.objects.filter(module__formation__in=paths).count(), 38)
        self.assertEqual(ModuleQuizQuestion.objects.filter(module__formation__in=paths).count(), 57)
        self.assertTrue(all(
            module.quiz_questions.count() == 3
            for module in CourseModule.objects.filter(formation__in=paths)
        ))
        intermediate_paths = paths.filter(level='Intermédiaire')
        self.assertEqual(intermediate_paths.count(), 4)
        intermediate_lessons = CourseLesson.objects.filter(module__formation__in=intermediate_paths)
        self.assertEqual(intermediate_lessons.count(), 24)
        self.assertTrue(all(
            'Atelier pratique guidé' in lesson.exercise
            and 'Livrable attendu :' in lesson.exercise
            and 'Critères de réussite :' in lesson.exercise
            for lesson in intermediate_lessons
        ))
        self.assertTrue(all(path.prerequisites and path.project_outcome for path in intermediate_paths))
        self.assertTrue(all(path.modules.count() == 3 for path in intermediate_paths))
        self.assertEqual(
            set(intermediate_paths.values_list('title', flat=True)),
            {
                'Développer une API professionnelle avec Django REST',
                'Cybersécurité défensive : analyser et répondre aux incidents',
                'Data Analytics : transformer un jeu de données en décision',
                'DevOps : automatiser les tests et livrer une application',
            },
        )
        self.assertTrue(all(
            path.modules.first().lessons.count() == 2
            for path in intermediate_paths
        ))

    def test_public_course_detail_locks_lessons_until_enrollment(self):
        path = Formation.objects.get(title='Python pratique : les fondamentaux')

        public_response = self.client.get(f'/api/formations/{path.id}/')

        self.assertEqual(public_response.status_code, 200)
        self.assertTrue(public_response.data['hosted_by_jupython'])
        self.assertEqual(len(public_response.data['modules']), 3)
        self.assertEqual(public_response.data['modules'][0]['lesson_count'], 2)
        self.assertEqual(len(public_response.data['modules'][0]['lessons']), 2)
        preview_lesson = public_response.data['modules'][0]['lessons'][0]
        self.assertTrue(preview_lesson['content_locked'])
        self.assertEqual(preview_lesson['content'], '')
        self.assertLessEqual(len(preview_lesson['content_preview']), 180)
        self.assertEqual(preview_lesson['exercise'], '')
        self.assertEqual(preview_lesson['learning_objectives'], [])

        user = User.objects.create_user(
            username='connected-course-reader',
            email='connected-course-reader@example.com',
            password='StrongPass123',
            university='UPN',
        )
        self.client.force_authenticate(user=user)
        authenticated_response = self.client.get(f'/api/formations/{path.id}/')
        authenticated_lesson = authenticated_response.data['modules'][0]['lessons'][0]
        self.assertEqual(authenticated_response.status_code, 200)
        self.assertFalse(authenticated_lesson['content_locked'])
        self.assertTrue(authenticated_lesson['content'])
        self.assertTrue(authenticated_lesson['learning_objectives'])

        enrolled_user = User.objects.create_user(
            username='course-student',
            email='course-student@example.com',
            password='StrongPass123',
            university='UPN',
        )
        Enrollment.objects.create(user=enrolled_user, formation=path)
        self.client.force_authenticate(user=enrolled_user)
        enrolled_response = self.client.get(f'/api/formations/{path.id}/')

        self.assertEqual(enrolled_response.status_code, 200)
        self.assertEqual(len(enrolled_response.data['modules'][0]['lessons']), 2)
        self.assertEqual(enrolled_response.data['modules'][0]['quiz_count'], 3)
        self.assertEqual(len(enrolled_response.data['modules'][1]['lessons']), 2)
        enrolled_lesson = enrolled_response.data['modules'][0]['lessons'][0]
        self.assertFalse(enrolled_lesson['content_locked'])
        self.assertEqual(enrolled_lesson['content_preview'], '')
        self.assertTrue(enrolled_lesson['content'])
        self.assertTrue(enrolled_lesson['exercise'])

    def test_intermediate_course_exposes_guided_practice_to_authenticated_learners(self):
        course = Formation.objects.get(
            title='DevOps : automatiser les tests et livrer une application',
        )
        user = User.objects.create_user(
            username='guided-practice-learner',
            email='guided-practice@example.com',
            password='StrongPass123',
            university='UPN',
        )
        self.client.force_authenticate(user=user)

        response = self.client.get(f'/api/formations/{course.id}/')

        self.assertEqual(response.status_code, 200)
        lessons = [
            lesson
            for module in response.data['modules']
            for lesson in module['lessons']
        ]
        self.assertEqual(len(lessons), 6)
        self.assertTrue(all(
            'Atelier pratique guidé' in lesson['exercise']
            and 'Livrable attendu :' in lesson['exercise']
            and 'Critères de réussite :' in lesson['exercise']
            for lesson in lessons
        ))

    def test_intermediate_api_course_exposes_prerequisites_and_project(self):
        course = Formation.objects.get(title='Développer une API professionnelle avec Django REST')

        response = self.client.get(f'/api/formations/{course.id}/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['level'], 'Intermédiaire')
        self.assertIn('Python', response.data['prerequisites'])
        self.assertIn('API', response.data['project_outcome'])
        self.assertEqual(len(response.data['modules']), 3)
        self.assertEqual(len(response.data['modules'][0]['lessons']), 2)
        self.assertIn(
            'request.user',
            CourseLesson.objects.get(
                module__formation=course,
                title='Filtrer par utilisateur et appliquer les permissions',
            ).content,
        )


class EnrollmentAccessTests(APITestCase):
    def test_enrollment_endpoints_require_authentication(self):
        enroll_response = self.client.post(
            '/api/enrollments/enroll/',
            {'formation_id': 1},
            format='json',
        )
        my_enrollments_response = self.client.get('/api/enrollments/my/')

        self.assertEqual(enroll_response.status_code, 401)
        self.assertEqual(my_enrollments_response.status_code, 401)


class EnrollmentProgressTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='StrongPass123',
            university='UPN',
        )
        self.other_user = User.objects.create_user(
            username='other-student',
            email='other@example.com',
            password='StrongPass123',
            university='UPN',
        )
        self.formation = Formation.objects.create(
            title='Python Basics',
            platform='Cisco',
            link='https://example.com/python',
        )
        self.enrollment = Enrollment.objects.create(user=self.user, formation=self.formation)

    def test_student_can_enroll_and_view_their_course(self):
        self.client.force_authenticate(user=self.user)
        self.enrollment.delete()

        enrollment_response = self.client.post(
            '/api/enrollments/enroll/',
            {'formation_id': self.formation.id},
            format='json',
        )
        my_enrollments_response = self.client.get('/api/enrollments/my/')

        self.assertEqual(enrollment_response.status_code, 200)
        self.assertTrue(enrollment_response.data['enrolled'])
        self.assertEqual(my_enrollments_response.status_code, 200)
        self.assertEqual(len(my_enrollments_response.data), 1)
        self.assertEqual(my_enrollments_response.data[0]['status'], Enrollment.STATUS_ENROLLED)
        self.assertEqual(my_enrollments_response.data[0]['formation']['title'], self.formation.title)
        self.assertFalse(my_enrollments_response.data[0]['formation']['hosted_by_jupython'])

    def test_reenrolling_preserves_the_existing_enrollment_and_progress(self):
        self.client.force_authenticate(user=self.user)
        lesson = CourseLesson.objects.create(
            module=CourseModule.objects.create(formation=self.formation, title='Module suivi'),
            title='Leçon suivie',
            content='Contenu',
        )
        LessonProgress.objects.create(user=self.user, lesson=lesson)
        original_enrollment_id = self.enrollment.id

        first_response = self.client.post(
            '/api/enrollments/enroll/',
            {'formation_id': self.formation.id},
            format='json',
        )
        second_response = self.client.post(
            '/api/enrollments/enroll/',
            {'formation_id': self.formation.id},
            format='json',
        )

        self.assertEqual(first_response.status_code, 200)
        self.assertFalse(first_response.data['enrolled'])
        self.assertTrue(first_response.data['already_enrolled'])
        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(Enrollment.objects.filter(user=self.user, formation=self.formation).count(), 1)
        self.assertEqual(Enrollment.objects.get(user=self.user, formation=self.formation).id, original_enrollment_id)
        self.assertTrue(LessonProgress.objects.filter(user=self.user, lesson=lesson).exists())

    def test_student_can_update_their_course_status(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            f'/api/enrollments/{self.enrollment.id}/progress/',
            {'status': Enrollment.STATUS_COMPLETED},
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], Enrollment.STATUS_COMPLETED)
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.status, Enrollment.STATUS_COMPLETED)

    def test_student_cannot_update_another_students_course_status(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.patch(
            f'/api/enrollments/{self.enrollment.id}/progress/',
            {'status': Enrollment.STATUS_COMPLETED},
            format='json',
        )

        self.assertEqual(response.status_code, 404)
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.status, Enrollment.STATUS_ENROLLED)


class CertificateSubmissionTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='StrongPass123',
            university='UPN',
        )
        self.formation = Formation.objects.create(
            title='Cybersecurity Basics',
            platform='Cisco',
            link='https://example.com/cybersecurity',
        )
        self.client.force_authenticate(user=self.user)

    def test_certificate_submission_does_not_require_jupython_enrollment(self):
        response = self.client.post(
            '/api/certificates/submit/',
            {
                'formation_id': self.formation.id,
                'certificate_url': 'https://example.com/certificate',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Certificate.objects.count(), 1)

    @patch('academy.certificates_api.send_n8n_event')
    def test_submitted_certificate_waits_for_manual_verification(self, send_event):
        Enrollment.objects.create(user=self.user, formation=self.formation)

        response = self.client.post(
            '/api/certificates/submit/',
            {'formation_id': self.formation.id, 'certificate_url': 'https://example.com/certificate'},
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertFalse(response.data['verified'])
        self.assertIn('seul l’organisme émetteur', response.data['verification_scope'])
        self.assertFalse(Certificate.objects.get().verified)
        send_event.assert_called_once()

    def test_certificate_submission_rejects_jupython_hosted_courses(self):
        self.formation.hosted_by_jupython = True
        self.formation.save(update_fields=['hosted_by_jupython'])
        Enrollment.objects.create(user=self.user, formation=self.formation)

        response = self.client.post(
            '/api/certificates/submit/',
            {'formation_id': self.formation.id, 'certificate_url': 'https://example.com/certificate'},
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('ne délivre pas de certificat', response.data['error'])
        self.assertEqual(Certificate.objects.count(), 0)

    def test_certificate_submission_rejects_non_https_links(self):
        Enrollment.objects.create(user=self.user, formation=self.formation)

        response = self.client.post(
            '/api/certificates/submit/',
            {'formation_id': self.formation.id, 'certificate_url': 'http://example.com/certificate'},
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Certificate.objects.count(), 0)

    def test_user_can_submit_and_download_a_private_pdf_certificate(self):
        Enrollment.objects.create(user=self.user, formation=self.formation)
        response = self.client.post(
            '/api/certificates/submit/',
            {
                'formation_id': self.formation.id,
                'certificate_file': SimpleUploadedFile(
                    'certificate.pdf',
                    b'%PDF-1.4\nJupython certificate test',
                    content_type='application/pdf',
                ),
            },
            format='multipart',
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data['certificate_file_available'])
        certificate = Certificate.objects.get()
        self.addCleanup(certificate.certificate_file.delete, save=False)
        self.assertFalse(certificate.certificate_url)

        download = self.client.get(f'/api/certificates/{certificate.id}/file/')
        self.assertEqual(download.status_code, 200)
        self.assertEqual(download['Content-Type'], 'application/pdf')
        self.assertIn(b'%PDF-1.4', b''.join(download.streaming_content))

    def test_certificate_file_is_private_to_its_owner(self):
        Enrollment.objects.create(user=self.user, formation=self.formation)
        response = self.client.post(
            '/api/certificates/submit/',
            {
                'formation_id': self.formation.id,
                'certificate_file': SimpleUploadedFile(
                    'certificate.pdf',
                    b'%PDF-1.4\nPrivate test',
                    content_type='application/pdf',
                ),
            },
            format='multipart',
        )
        certificate = Certificate.objects.get()
        self.addCleanup(certificate.certificate_file.delete, save=False)
        self.assertEqual(response.status_code, 201)

        other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='StrongPass123',
        )
        self.client.force_authenticate(user=other_user)
        self.assertEqual(
            self.client.get(f'/api/certificates/{certificate.id}/file/').status_code,
            404,
        )

    def test_certificate_file_rejects_invalid_pdf(self):
        Enrollment.objects.create(user=self.user, formation=self.formation)
        response = self.client.post(
            '/api/certificates/submit/',
            {
                'formation_id': self.formation.id,
                'certificate_file': SimpleUploadedFile(
                    'certificate.pdf',
                    b'not a PDF',
                    content_type='application/pdf',
                ),
            },
            format='multipart',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Certificate.objects.count(), 0)

    def test_user_can_submit_a_png_certificate(self):
        Enrollment.objects.create(user=self.user, formation=self.formation)
        image_buffer = BytesIO()
        Image.new('RGB', (3, 3), color='orange').save(image_buffer, format='PNG')
        response = self.client.post(
            '/api/certificates/submit/',
            {
                'formation_id': self.formation.id,
                'certificate_file': SimpleUploadedFile(
                    'certificate.png',
                    image_buffer.getvalue(),
                    content_type='image/png',
                ),
            },
            format='multipart',
        )
        self.assertEqual(response.status_code, 201)
        certificate = Certificate.objects.get()
        self.addCleanup(certificate.certificate_file.delete, save=False)
        download = self.client.get(f'/api/certificates/{certificate.id}/file/')
        self.assertEqual(download.status_code, 200)
        self.assertEqual(download['Content-Type'], 'image/png')
        self.assertTrue(b''.join(download.streaming_content).startswith(b'\x89PNG'))

    def test_staff_can_review_uploaded_certificate_in_admin(self):
        Enrollment.objects.create(user=self.user, formation=self.formation)
        response = self.client.post(
            '/api/certificates/submit/',
            {
                'formation_id': self.formation.id,
                'certificate_file': SimpleUploadedFile(
                    'certificate.pdf',
                    b'%PDF-1.4\nStaff review test',
                    content_type='application/pdf',
                ),
            },
            format='multipart',
        )
        self.assertEqual(response.status_code, 201)
        certificate = Certificate.objects.get()
        self.addCleanup(certificate.certificate_file.delete, save=False)
        staff_user = User.objects.create_superuser(
            username='reviewer',
            email='reviewer@example.com',
            password='StrongPass123',
        )
        self.client.force_authenticate(user=None)
        self.client.force_login(staff_user)
        download = self.client.get(
            f'/admin/academy/certificate/{certificate.id}/download-certificate/'
        )
        self.assertEqual(download.status_code, 200)
        self.assertIn(b'%PDF-1.4', b''.join(download.streaming_content))


class LessonProgressTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='StrongPass123',
            university='UPN',
        )
        self.other_user = User.objects.create_user(
            username='other-student',
            email='other@example.com',
            password='StrongPass123',
            university='UPN',
        )
        self.formation = Formation.objects.create(
            title='Cours Jupython de test',
            platform='Jupython',
            link='https://jupython.cd/academy/learn.html',
            hosted_by_jupython=True,
        )
        self.module = CourseModule.objects.create(
            formation=self.formation,
            title='Module de test',
            order=1,
        )
        self.lesson = CourseLesson.objects.create(
            module=self.module,
            title='Leçon de test',
            content='Contenu de la leçon.',
            order=1,
        )

    def test_lesson_progress_requires_enrollment(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(f'/api/enrollments/lessons/{self.lesson.id}/progress/')

        self.assertEqual(response.status_code, 403)
        self.assertEqual(LessonProgress.objects.count(), 0)

    def test_student_can_complete_and_reopen_own_lesson(self):
        self.client.force_authenticate(user=self.user)
        Enrollment.objects.create(user=self.user, formation=self.formation)
        LessonPracticeSubmission.objects.create(
            user=self.user,
            lesson=self.lesson,
            response='Travail de test approuvé',
            status=LessonPracticeSubmission.STATUS_APPROVED,
        )

        complete_response = self.client.post(f'/api/enrollments/lessons/{self.lesson.id}/progress/')
        enrollment = Enrollment.objects.get(user=self.user, formation=self.formation)
        reopen_response = self.client.delete(f'/api/enrollments/lessons/{self.lesson.id}/progress/')

        self.assertEqual(complete_response.status_code, 200)
        self.assertEqual(complete_response.data['percent'], 100)
        self.assertEqual(enrollment.status, Enrollment.STATUS_COMPLETED)
        self.assertEqual(reopen_response.status_code, 200)
        self.assertEqual(reopen_response.data['percent'], 0)
        self.assertEqual(Enrollment.objects.get(id=enrollment.id).status, Enrollment.STATUS_ENROLLED)
        self.assertFalse(LessonProgress.objects.filter(user=self.user, lesson=self.lesson).exists())

    def test_student_cannot_complete_another_students_lesson(self):
        self.client.force_authenticate(user=self.other_user)
        Enrollment.objects.create(user=self.user, formation=self.formation)

        response = self.client.post(f'/api/enrollments/lessons/{self.lesson.id}/progress/')

        self.assertEqual(response.status_code, 403)
        self.assertFalse(LessonProgress.objects.exists())

    def test_module_test_is_required_to_unlock_the_next_module(self):
        self.client.force_authenticate(user=self.user)
        Enrollment.objects.create(user=self.user, formation=self.formation)
        next_module = CourseModule.objects.create(
            formation=self.formation,
            title='Module suivant',
            order=2,
        )
        next_lesson = CourseLesson.objects.create(
            module=next_module,
            title='Leçon suivante',
            content='Contenu suivant',
        )
        questions = [
            ModuleQuizQuestion.objects.create(
                module=self.module,
                prompt=f'Question {index}',
                choices=['A', 'B', 'C'],
                correct_choice=index % 3,
                order=index,
            )
            for index in range(1, 4)
        ]
        LessonPracticeSubmission.objects.create(
            user=self.user,
            lesson=self.lesson,
            response='Travail de test approuvé',
            status=LessonPracticeSubmission.STATUS_APPROVED,
        )

        locked_response = self.client.post(f'/api/enrollments/lessons/{next_lesson.id}/progress/')
        quiz_before_lessons_response = self.client.get(f'/api/enrollments/modules/{self.module.id}/quiz/')
        self.client.post(f'/api/enrollments/lessons/{self.lesson.id}/progress/')
        quiz_before_test_response = self.client.get(f'/api/enrollments/modules/{self.module.id}/quiz/')
        failed_answers = {str(question.id): (question.correct_choice + 1) % 3 for question in questions}
        failed_attempt = self.client.post(
            f'/api/enrollments/modules/{self.module.id}/quiz/',
            {'answers': failed_answers},
            format='json',
        )
        still_locked_response = self.client.post(f'/api/enrollments/lessons/{next_lesson.id}/progress/')
        passing_answers = {
            str(question.id): question.correct_choice if index < 2 else (question.correct_choice + 1) % 3
            for index, question in enumerate(questions)
        }
        passed_attempt = self.client.post(
            f'/api/enrollments/modules/{self.module.id}/quiz/',
            {'answers': passing_answers},
            format='json',
        )
        LessonPracticeSubmission.objects.create(
            user=self.user,
            lesson=next_lesson,
            response='Travail de test approuvé',
            status=LessonPracticeSubmission.STATUS_APPROVED,
        )
        unlocked_response = self.client.post(f'/api/enrollments/lessons/{next_lesson.id}/progress/')

        self.assertEqual(locked_response.status_code, 403)
        self.assertEqual(quiz_before_lessons_response.status_code, 409)
        self.assertEqual(quiz_before_test_response.status_code, 200)
        self.assertNotIn('correct_choice', quiz_before_test_response.data['questions'][0])
        self.assertEqual(failed_attempt.data['score'], 0)
        self.assertFalse(failed_attempt.data['passed'])
        self.assertEqual(still_locked_response.status_code, 403)
        self.assertEqual(passed_attempt.data['score'], 67)
        self.assertTrue(passed_attempt.data['passed'])
        self.assertEqual(passed_attempt.data['attempts'], 2)
        self.assertIn(self.module.id, passed_attempt.data['passed_module_ids'])
        self.assertEqual(unlocked_response.status_code, 200)
        self.assertEqual(ModuleQuizProgress.objects.get(user=self.user, module=self.module).attempts, 2)
        curriculum_response = self.client.get(f'/api/formations/{self.formation.id}/')
        self.assertEqual(len(curriculum_response.data['modules'][1]['lessons']), 1)
