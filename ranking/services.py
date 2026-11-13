from django.db.models import BooleanField, Count, Exists, F, IntegerField, OuterRef, Subquery, Value

from accounts.models import User, UserFollow
from .models import LeaderboardSnapshot


def get_public_member_directory(current_user=None):
    users = User.objects.filter(is_active=True).annotate(
        follower_count=Count('followers', distinct=True),
        leaderboard_score=Subquery(
            LeaderboardSnapshot.objects.filter(user_id=OuterRef('pk'))
            .order_by('-created_at')
            .values('score')[:1],
            output_field=IntegerField(),
        ),
    )
    if current_user and current_user.is_authenticated:
        users = users.annotate(
            is_following=Exists(
                UserFollow.objects.filter(follower=current_user, followed_id=OuterRef('pk'))
            )
        )
    else:
        users = users.annotate(is_following=Value(False, output_field=BooleanField()))

    return [
        {
            'id': user.id,
            'display_name': user.profile_display_name,
            'bio': user.bio,
            'avatar': user.avatar.url if user.avatar else '',
            'follower_count': user.follower_count,
            'is_following': user.is_following,
            'score': user.leaderboard_score,
        }
        for user in users.only(
            'id', 'first_name', 'last_name', 'public_name', 'bio', 'avatar',
        ).order_by(F('leaderboard_score').desc(nulls_last=True), '-follower_count', 'id')
    ]
