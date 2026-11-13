import re

from rest_framework import serializers
from .models import CourseLesson, CourseModule, Enrollment, Formation, LessonProgress, ModuleQuizProgress


class CourseLessonSerializer(serializers.ModelSerializer):
    content = serializers.SerializerMethodField()
    content_preview = serializers.SerializerMethodField()
    content_locked = serializers.SerializerMethodField()
    exercise = serializers.SerializerMethodField()
    learning_objectives = serializers.SerializerMethodField()

    def _is_authenticated(self):
        request = self.context.get('request')
        return bool(request and request.user.is_authenticated)

    def get_content(self, lesson):
        return lesson.content if self._is_authenticated() else ''

    def get_content_preview(self, lesson):
        if self._is_authenticated():
            return ''
        preview = re.sub(r'\s+', ' ', lesson.content).strip()
        if len(preview) > 180:
            return f'{preview[:177].rstrip()}...'
        return preview

    def get_content_locked(self, lesson):
        return not self._is_authenticated()

    def get_exercise(self, lesson):
        return lesson.exercise if self._is_authenticated() else ''

    def get_learning_objectives(self, lesson):
        return lesson.learning_objectives if self._is_authenticated() else []

    class Meta:
        model = CourseLesson
        fields = [
            'id',
            'title',
            'content',
            'content_preview',
            'content_locked',
            'exercise',
            'learning_objectives',
            'duration_minutes',
            'order',
        ]


class CourseModuleSerializer(serializers.ModelSerializer):
    lessons = serializers.SerializerMethodField()
    lesson_count = serializers.SerializerMethodField()
    quiz_count = serializers.SerializerMethodField()
    quiz_questions = serializers.SerializerMethodField()

    def get_lessons(self, module):
        return CourseLessonSerializer(module.lessons.all(), many=True, context=self.context).data

    @staticmethod
    def get_lesson_count(module):
        return len(module.lessons.all())

    @staticmethod
    def get_quiz_count(module):
        return len(module.quiz_questions.all())

    def get_quiz_questions(self, module):
        if (
            module.formation.hosted_by_jupython
            and module.id not in self.context.get('quiz_accessible_module_ids', set())
        ):
            return []
        return [
            {
                'id': question.id,
                'prompt': question.prompt,
                'choices': question.choices,
                'order': question.order,
            }
            for question in module.quiz_questions.all()
        ]

    class Meta:
        model = CourseModule
        fields = [
            'id',
            'title',
            'description',
            'order',
            'lesson_count',
            'quiz_count',
            'lessons',
            'quiz_questions',
        ]


class FormationSerializer(serializers.ModelSerializer):
    modules = CourseModuleSerializer(many=True, read_only=True)

    class Meta:
        model = Formation
        fields = '__all__'
