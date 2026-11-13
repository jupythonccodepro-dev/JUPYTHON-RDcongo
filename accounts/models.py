import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser


def avatar_upload_path(instance, filename):
    extension = filename.rsplit('.', 1)[-1].lower() if '.' in filename else 'jpg'
    return f'avatars/{instance.pk}/{uuid.uuid4().hex}.{extension}'


class User(AbstractUser):
    university = models.CharField(max_length=255, blank=True)
    promotion = models.CharField(max_length=50, blank=True)

    public_name = models.CharField(max_length=60, blank=True)
    bio = models.CharField(max_length=280, blank=True)
    avatar = models.ImageField(upload_to=avatar_upload_path, blank=True)

    @property
    def profile_display_name(self):
        if self.public_name.strip():
            return self.public_name.strip()
        full_name = self.get_full_name().strip()
        return full_name or 'Membre Jupython'

    def __str__(self):
        return self.username


class UserFollow(models.Model):
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )
    followed = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['follower', 'followed'],
                name='unique_user_follow',
            ),
            models.CheckConstraint(
                condition=~models.Q(follower=models.F('followed')),
                name='prevent_self_follow',
            ),
        ]
        ordering = ['-created_at']