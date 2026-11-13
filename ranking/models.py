from django.db import models


class LeaderboardSnapshot(models.Model):
    """A lightweight snapshot of a ranking state used for reporting or analytics."""
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-score', '-created_at']

    def __str__(self):
        return f'{self.user} - {self.score}'
