from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Enrollment, Formation, LessonProgress, ModuleQuizProgress
from .serializers import FormationSerializer
from .permissions import IsAdminOrReadOnly


class FormationViewSet(ModelViewSet):
    serializer_class = FormationSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return Formation.objects.prefetch_related('modules__lessons', 'modules__quiz_questions').all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        request = context['request']
        user = request.user
        context['quiz_accessible_module_ids'] = set()
        if not user.is_authenticated:
            return context

        enrolled_formation_ids = set(
            Enrollment.objects.filter(
                user=user,
                formation__hosted_by_jupython=True,
            ).values_list('formation_id', flat=True)
        )
        if not enrolled_formation_ids:
            return context

        completed_lesson_ids = set(
            LessonProgress.objects.filter(
                user=user,
                lesson__module__formation_id__in=enrolled_formation_ids,
            ).values_list('lesson_id', flat=True)
        )
        passed_module_ids = set(
            ModuleQuizProgress.objects.filter(
                user=user,
                module__formation_id__in=enrolled_formation_ids,
                passed=True,
            ).values_list('module_id', flat=True)
        )
        modules = Formation.objects.filter(id__in=enrolled_formation_ids).prefetch_related(
            'modules__lessons',
        )
        unlocked_module_ids = set()
        quiz_accessible_module_ids = set()
        for formation in modules:
            previous_module = None
            previous_unlocked = True
            for module in formation.modules.all():
                module_unlocked = previous_module is None or (
                    previous_unlocked
                    and previous_module.id in passed_module_ids
                    and previous_module.lessons.exists()
                    and all(
                        lesson.id in completed_lesson_ids
                        for lesson in previous_module.lessons.all()
                    )
                )
                if module_unlocked:
                    unlocked_module_ids.add(module.id)
                    lesson_ids = {lesson.id for lesson in module.lessons.all()}
                    if lesson_ids and lesson_ids <= completed_lesson_ids:
                        quiz_accessible_module_ids.add(module.id)
                previous_module = module
                previous_unlocked = module_unlocked
        context['quiz_accessible_module_ids'] = quiz_accessible_module_ids
        return context

    def perform_create(self, serializer):
        # Seuls les membres du personnel peuvent créer des formations ; la classe de permissions l’impose déjà.
        serializer.save()
