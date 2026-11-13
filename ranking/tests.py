from django.test import TestCase

from accounts.models import User, UserFollow
from academy.models import Certificate, Formation
from ranking.models import LeaderboardSnapshot
from ranking.services import get_public_member_directory


class RankingComputationTests(TestCase):
    def test_member_directory_never_exposes_private_profile_data(self):
        user_one = User.objects.create_user(username='u1', email='u1@example.com', password='StrongPass123')
        user_two = User.objects.create_user(username='u2', email='u2@example.com', password='StrongPass123')
        formation = Formation.objects.create(title='Django', platform='Udemy', link='https://example.com')

        Certificate.objects.create(user=user_one, formation=formation, certificate_url='https://example.com/cert-1', verified=True)

        members = get_public_member_directory()
        result = next(row for row in members if row['id'] == user_one.id)

        self.assertEqual(result['display_name'], 'Membre Jupython')
        self.assertEqual(
            set(result),
            {'id', 'display_name', 'bio', 'avatar', 'follower_count', 'is_following', 'score'},
        )
        self.assertEqual(result['follower_count'], 0)
        self.assertFalse(result['is_following'])
        self.assertIsNone(result['score'])
        self.assertNotIn('email', result)
        self.assertNotIn('university', result)

    def test_member_directory_marks_followed_users_and_orders_by_followers(self):
        current_user = User.objects.create_user(
            username='current',
            email='current@example.com',
            password='StrongPass123',
        )
        followed_user = User.objects.create_user(
            username='followed',
            email='followed@example.com',
            password='StrongPass123',
        )
        popular_user = User.objects.create_user(
            username='popular',
            email='popular@example.com',
            password='StrongPass123',
        )
        another_follower = User.objects.create_user(
            username='another',
            email='another@example.com',
            password='StrongPass123',
        )
        UserFollow.objects.create(follower=current_user, followed=followed_user)
        UserFollow.objects.create(follower=another_follower, followed=popular_user)
        UserFollow.objects.create(follower=current_user, followed=popular_user)

        members = get_public_member_directory(current_user)

        self.assertEqual(members[0]['id'], popular_user.id)
        self.assertEqual(members[0]['follower_count'], 2)
        self.assertTrue(members[0]['is_following'])
        followed_result = next(row for row in members if row['id'] == followed_user.id)
        self.assertEqual(followed_result['follower_count'], 1)
        self.assertTrue(followed_result['is_following'])
        current_result = next(row for row in members if row['id'] == current_user.id)
        self.assertFalse(current_result['is_following'])

    def test_member_directory_orders_users_by_latest_leaderboard_score(self):
        lower_score = User.objects.create_user(
            username='lower-score',
            email='lower-score@example.com',
            password='StrongPass123',
        )
        higher_score = User.objects.create_user(
            username='higher-score',
            email='higher-score@example.com',
            password='StrongPass123',
        )
        LeaderboardSnapshot.objects.create(user=lower_score, score=15)
        LeaderboardSnapshot.objects.create(user=higher_score, score=90)

        members = get_public_member_directory()

        self.assertEqual(members[0]['id'], higher_score.id)
        self.assertEqual(members[0]['score'], 90)
        self.assertEqual(members[1]['id'], lower_score.id)
        self.assertEqual(members[1]['score'], 15)
