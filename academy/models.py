import uuid

from django.db import models
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible

# Utiliser le modèle utilisateur configuré (sous forme de chaîne via settings.AUTH_USER_MODEL).
User = settings.AUTH_USER_MODEL


@deconstructible
class PrivateCertificateStorage(FileSystemStorage):
    def __init__(self, location=None):
        super().__init__(location=location or settings.PRIVATE_CERTIFICATES_ROOT)


certificate_storage = PrivateCertificateStorage()


def certificate_upload_path(instance, filename):
    extension = filename.rsplit('.', 1)[-1].lower() if '.' in filename else 'bin'
    return f'certificates/{uuid.uuid4().hex}.{extension}'


class Academy(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    platform = models.CharField(max_length=100)
    link = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


# Modèles supplémentaires pour rester cohérent avec le backend de référence.
class Formation(models.Model):
    title = models.CharField(max_length=200)
    platform = models.CharField(max_length=100)
    link = models.URLField()
    is_free = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    domain = models.CharField(max_length=100, blank=True)
    level = models.CharField(max_length=50, blank=True)
    duration = models.CharField(max_length=100, blank=True)
    language = models.CharField(max_length=100, blank=True)
    skills = models.JSONField(default=list, blank=True)
    credential_info = models.TextField(blank=True)
    hosted_by_jupython = models.BooleanField(default=False)
    cover_image = models.ImageField(
        upload_to='academy/course-covers/',
        blank=True,
        help_text='Visuel cr?? ou fourni par Jupython, pour les cours internes.',
    )
    cover_image_url = models.URLField(
        blank=True,
        help_text='URL HTTPS du visuel officiel du cours externe, provenant du site fournisseur.',
    )
    provider_logo_url = models.URLField(
        blank=True,
        help_text='URL HTTPS du logo officiel du fournisseur externe.',
    )
    last_verified_at = models.DateTimeField(null=True, blank=True)
    prerequisites = models.TextField(blank=True)
    project_outcome = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    STATUS_ENROLLED = 'enrolled'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'
    STATUS_CHOICES = [
        (STATUS_ENROLLED, 'Inscrit'),
        (STATUS_IN_PROGRESS, 'En cours'),
        (STATUS_COMPLETED, 'Terminé'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE)
    date_joined = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ENROLLED)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'formation'], name='unique_user_formation_enrollment')
        ]
        ordering = ['-date_joined']

    def __str__(self):
        return f'{self.user} -> {self.formation}'


class CourseModule(models.Model):
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.formation.title} — {self.title}'


class CourseLesson(models.Model):
    module = models.ForeignKey(CourseModule, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = models.TextField()
    exercise = models.TextField(blank=True)
    learning_objectives = models.JSONField(default=list, blank=True)
    duration_minutes = models.PositiveIntegerField(default=15)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.title


class ModuleQuizQuestion(models.Model):
    module = models.ForeignKey(CourseModule, on_delete=models.CASCADE, related_name='quiz_questions')
    prompt = models.TextField()
    choices = models.JSONField(default=list)
    correct_choice = models.PositiveSmallIntegerField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.module.title} — {self.prompt}'


class ModuleQuizProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='module_quiz_progress')
    module = models.ForeignKey(CourseModule, on_delete=models.CASCADE, related_name='quiz_progress')
    attempts = models.PositiveIntegerField(default=0)
    best_score = models.PositiveSmallIntegerField(default=0)
    passed = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'module'], name='unique_user_module_quiz_progress')
        ]

    def __str__(self):
        return f'{self.user} — {self.module.title} ({self.best_score}%)'


class LessonProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(CourseLesson, on_delete=models.CASCADE, related_name='progress_records')
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'lesson'], name='unique_user_lesson_progress')
        ]
        ordering = ['completed_at']

    def __str__(self):
        return f'{self.user} — {self.lesson}'


class LessonPracticeSubmission(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_REVISION = 'revision'
    STATUS_APPROVED = 'approved'
    STATUS_CHOICES = [
        (STATUS_PENDING, '? corriger'),
        (STATUS_REVISION, '? refaire'),
        (STATUS_APPROVED, 'Valid?e'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_practice_submissions')
    lesson = models.ForeignKey(CourseLesson, on_delete=models.CASCADE, related_name='practice_submissions')
    response = models.TextField(verbose_name='R?ponse ou lien vers le travail')
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_PENDING)
    feedback = models.TextField(blank=True, verbose_name='Retour au participant')
    submitted_at = models.DateTimeField(auto_now=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewer = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name='reviewed_practice_submissions'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'lesson'], name='unique_user_lesson_practice_submission')
        ]
        ordering = ['status', 'submitted_at']
        verbose_name = 'Remise de pratique'
        verbose_name_plural = 'Remises de pratique'

    def __str__(self):
        return f'{self.user} ? {self.lesson} ({self.get_status_display()})'


class Certificate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE)
    certificate_url = models.URLField(
        blank=True,
        verbose_name='Lien du justificatif (URL HTTPS)',
        help_text='Lien HTTPS vers un justificatif émis par le fournisseur de la formation.',
    )
    certificate_file = models.FileField(
        storage=certificate_storage,
        upload_to=certificate_upload_path,
        blank=True,
        verbose_name='Fichier du justificatif',
    )
    verified = models.BooleanField(
        verbose_name='Justificatif examiné par Jupython',
        default=False,
        help_text=(
            'Indique que Jupython a examiné le justificatif soumis. '
            'Cela n’implique pas une validation de l’émetteur : seul l’organisme ayant délivré le document peut confirmer son authenticité.'
        ),
    )
    issued_at = models.DateTimeField(null=True, blank=True, verbose_name='Date d’émission')
    verified_at = models.DateTimeField(null=True, blank=True, verbose_name='Date d’examen')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'formation'], name='unique_user_formation_certificate')
        ]
        ordering = ['-issued_at', '-verified_at']
        verbose_name = 'Justificatif'
        verbose_name_plural = 'Justificatifs'

    def __str__(self):
        # Représentation lisible en français pour l'admin et les logs
        formation_title = getattr(self.formation, 'title', str(self.formation))
        return f"Justificatif {self.id} — {self.user} — {formation_title}"
