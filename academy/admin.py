from datetime import timedelta

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import Http404
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils import timezone

from .models import (
    Academy,
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
from .certificates_api import certificate_file_response


class CourseLessonInline(admin.TabularInline):
    model = CourseLesson
    extra = 0


class ModuleQuizQuestionInline(admin.TabularInline):
    model = ModuleQuizQuestion
    extra = 0


class CourseModuleInline(admin.TabularInline):
    model = CourseModule
    extra = 0


class CourseReviewFilter(admin.SimpleListFilter):
    title = 'vérification du cours'
    parameter_name = 'review'

    def lookups(self, request, model_admin):
        return (
            ('stale', 'À revérifier (> 30 jours)'),
            ('current', 'Vérifié depuis moins de 30 jours'),
        )

    def queryset(self, request, queryset):
        stale_before = timezone.now() - timedelta(days=30)
        if self.value() == 'stale':
            return queryset.filter(
                Q(last_verified_at__isnull=True) | Q(last_verified_at__lt=stale_before),
            )
        if self.value() == 'current':
            return queryset.filter(last_verified_at__gte=stale_before)
        return queryset


@admin.action(description='Marquer les cours sélectionnés comme revérifiés')
def mark_courses_verified(modeladmin, request, queryset):
    queryset.update(last_verified_at=timezone.now())


@admin.register(Academy)
class AcademyAdmin(admin.ModelAdmin):
    list_display = ('title', 'platform', 'user', 'created_at')
    search_fields = ('title', 'platform', 'user__username')


@admin.register(Formation)
class FormationAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'platform',
        'domain',
        'level',
        'is_free',
        'hosted_by_jupython',
        'last_verified_at',
    )
    list_filter = ('platform', 'domain', 'level', 'is_free', 'hosted_by_jupython', CourseReviewFilter)
    search_fields = ('title', 'platform', 'domain', 'description')
    inlines = [CourseModuleInline]
    actions = [mark_courses_verified]


@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'formation', 'order')
    list_filter = ('formation__platform', 'formation')
    search_fields = ('title', 'formation__title')
    inlines = [CourseLessonInline, ModuleQuizQuestionInline]


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'formation', 'status', 'date_joined')
    list_filter = ('status', 'formation__platform')
    search_fields = ('user__username', 'formation__title')


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('user', 'formation', 'justificatif_examine', 'certificate_file_download', 'issued_at')
    list_filter = ('verified', 'formation__platform')
    search_fields = ('user__username', 'formation__title')

    def get_urls(self):
        custom_urls = [
            path(
                '<path:object_id>/download-certificate/',
                self.admin_site.admin_view(self.download_certificate),
                name='academy_certificate_download',
            ),
        ]
        return custom_urls + super().get_urls()

    def download_certificate(self, request, object_id):
        certificate = self.get_object(request, object_id)
        if certificate is None:
            raise Http404
        if not self.has_view_permission(request, certificate):
            raise PermissionDenied
        return certificate_file_response(certificate)

    @admin.display(description='Fichier')
    def certificate_file_download(self, certificate):
        if not certificate.certificate_file:
            return '—'
        url = reverse('admin:academy_certificate_download', args=[certificate.pk])
        return format_html('<a href="{}">Télécharger le justificatif</a>', url)

    @admin.display(boolean=True, description='Justificatif examiné par Jupython')
    def justificatif_examine(self, certificate):
        return certificate.verified


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'completed_at')
    list_filter = ('lesson__module__formation',)
    search_fields = ('user__username', 'lesson__title', 'lesson__module__formation__title')


@admin.register(LessonPracticeSubmission)
class LessonPracticeSubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'course_name', 'status', 'submitted_at', 'reviewer', 'reviewed_at')
    list_filter = ('status', 'lesson__module__formation')
    search_fields = ('user__username', 'user__email', 'lesson__title', 'lesson__module__formation__title')
    readonly_fields = ('user', 'lesson', 'response', 'submitted_at', 'reviewer', 'reviewed_at')
    fields = ('user', 'lesson', 'response', 'status', 'feedback', 'submitted_at', 'reviewer', 'reviewed_at')

    @admin.display(description='Formation')
    def course_name(self, submission):
        return submission.lesson.module.formation.title

    def save_model(self, request, obj, form, change):
        from django.utils import timezone

        obj.reviewer = request.user
        obj.reviewed_at = timezone.now()
        super().save_model(request, obj, form, change)
        if obj.status == LessonPracticeSubmission.STATUS_APPROVED:
            LessonProgress.objects.get_or_create(user=obj.user, lesson=obj.lesson)
        else:
            LessonProgress.objects.filter(user=obj.user, lesson=obj.lesson).delete()
        enrollment = Enrollment.objects.filter(user=obj.user, formation=obj.lesson.module.formation).first()
        if enrollment:
            from .enrollments_api import LessonProgressAPIView
            LessonProgressAPIView._update_enrollment_status(obj.user, obj.lesson.module.formation)


@admin.register(ModuleQuizProgress)
class ModuleQuizProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'module', 'best_score', 'passed', 'attempts', 'updated_at')
    list_filter = ('passed', 'module__formation')
    search_fields = ('user__username', 'module__title', 'module__formation__title')
