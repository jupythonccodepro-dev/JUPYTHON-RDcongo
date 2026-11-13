from datetime import datetime
from io import BytesIO
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.utils import timezone
from django.urls import reverse
from PIL import Image
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, UserFollow


class AuthFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_returns_tokens_for_new_user(self):
        response = self.client.post(
            reverse('register'),
            {
                'fullname': 'Jane Doe',
                'email': 'jane@example.com',
                'password': 'supersecret123',
                'university': 'UPN',
                'promotion': 'L1 Informatique',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['user']['promotion'], 'L1 Informatique')
        self.assertEqual(User.objects.get(email='jane@example.com').promotion, 'L1 Informatique')
        self.assertIn('access', response.json())
        self.assertIn('refresh', response.json())
        self.assertTrue(User.objects.filter(email='jane@example.com').exists())

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_password_reset_sends_link_and_changes_password(self):
        from django.core import mail

        user = User.objects.create_user(
            username='reset@example.com',
            email='reset@example.com',
            password='supersecret123',
        )
        response = self.client.post(
            reverse('password_reset'),
            {'email': user.email},
            format='json',
            HTTP_HOST='testserver',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        reset_url = mail.outbox[0].body.splitlines()[3]
        from urllib.parse import urlparse, parse_qs
        query = parse_qs(urlparse(reset_url).query)
        confirm_response = self.client.post(
            reverse('password_reset_confirm'),
            {
                'uid': query['uid'][0],
                'token': query['token'][0],
                'password': 'anothersecure456',
                'confirm_password': 'anothersecure456',
            },
            format='json',
        )
        self.assertEqual(confirm_response.status_code, 200)
        user.refresh_from_db()
        self.assertTrue(user.check_password('anothersecure456'))

    @override_settings(
        DEBUG=True,
        EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend',
    )
    def test_local_password_reset_explains_that_link_is_printed_in_server_terminal(self):
        from django.core import mail

        user = User.objects.create_user(
            username='local-reset@example.com',
            email='local-reset@example.com',
            password='supersecret123',
        )

        response = self.client.post(
            reverse('password_reset'),
            {'email': user.email},
            format='json',
            HTTP_HOST='testserver',
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('n’envoie pas de courriels', response.json()['message'])
        self.assertIn('terminal', response.json()['message'])
        self.assertEqual(len(mail.outbox), 0)

    def test_google_user_can_set_first_password_from_authenticated_profile(self):
        user = User.objects.create_user(
            username='google@example.com',
            email='google@example.com',
            password=None,
        )
        self.assertFalse(user.has_usable_password())
        self.client.force_authenticate(user=user)
        response = self.client.post(
            reverse('password_change'),
            {
                'current_password': '',
                'password': 'anothersecure456',
                'confirm_password': 'anothersecure456',
            },
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertTrue(user.check_password('anothersecure456'))

    def test_password_change_rotates_tokens_and_rejects_old_refresh(self):
        user = User.objects.create_user(
            username='change@example.com',
            email='change@example.com',
            password='supersecret123',
        )
        old_refresh = RefreshToken.for_user(user)
        self.client.force_authenticate(user=user)
        response = self.client.post(
            reverse('password_change'),
            {
                'current_password': 'supersecret123',
                'password': 'anothersecure456',
                'confirm_password': 'anothersecure456',
            },
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.json())
        self.assertIn('refresh', response.json())
        user.refresh_from_db()
        self.assertTrue(user.check_password('anothersecure456'))
        self.client.force_authenticate(user=None)
        refresh_response = self.client.post(
            reverse('token_refresh'),
            {'refresh': str(old_refresh)},
            format='json',
        )
        self.assertEqual(refresh_response.status_code, 401)

    def test_login_accepts_email_as_identifier(self):
        User.objects.create_user(
            username='jane@example.com',
            email='jane@example.com',
            password='supersecret123',
            university='UPN',
        )

        response = self.client.post(
            reverse('accounts_token_obtain_pair'),
            {
                'email': 'jane@example.com',
                'password': 'supersecret123',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.json())

    def test_refresh_token_can_renew_access_and_last_thirty_days(self):
        user = User.objects.create_user(
            username='persistent@example.com',
            email='persistent@example.com',
            password='supersecret123',
        )
        refresh = RefreshToken.for_user(user)
        remaining = datetime.fromtimestamp(
            int(refresh['exp']),
            tz=timezone.get_current_timezone(),
        ) - timezone.now()

        response = self.client.post(
            reverse('token_refresh'),
            {'refresh': str(refresh)},
            format='json',
        )

        self.assertGreaterEqual(remaining.days, 29)
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.json())
        self.assertIn('refresh', response.json())

    def test_register_rejects_weak_password(self):
        response = self.client.post(
            reverse('register'),
            {
                'fullname': 'Weak Password User',
                'email': 'weak@example.com',
                'password': '123',
                'university': 'UPN',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.json())

    def test_google_login_requires_id_token(self):
        response = self.client.post(reverse('google_login'), {}, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('id_token', response.json().get('error', ''))

    def test_login_page_allows_google_popup_to_message_opener(self):
        response = self.client.get('/academy/login.html')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Cross-Origin-Opener-Policy'],
            'same-origin-allow-popups',
        )

    @override_settings(GOOGLE_CLIENT_ID='')
    def test_google_login_reports_missing_configuration(self):
        response = self.client.post(
            reverse('google_login'),
            {'id_token': 'google-token'},
            format='json',
        )

        self.assertEqual(response.status_code, 501)
        self.assertIn('GOOGLE_CLIENT_ID', response.json()['error'])

    @patch('accounts.google_api._google_id_token.verify_oauth2_token')
    def test_google_login_explains_client_id_mismatch(self, verify_token):
        verify_token.side_effect = ValueError('Wrong recipient, payload audience does not match.')

        response = self.client.post(
            reverse('google_login'),
            {'id_token': 'not-logged-or-returned'},
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['code'], 'google_client_mismatch')
        self.assertNotIn('id_token', str(response.json()))

    @patch('accounts.google_api._google_id_token.verify_oauth2_token')
    def test_google_login_rejects_unverified_email(self, verify_token):
        verify_token.return_value = {
            'email': 'jane@example.com',
            'email_verified': False,
        }

        response = self.client.post(
            reverse('google_login'),
            {'id_token': 'not-logged-or-returned'},
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(User.objects.filter(email='jane@example.com').exists())

    @patch('accounts.google_api._google_id_token.verify_oauth2_token')
    def test_google_login_creates_user_for_verified_email(self, verify_token):
        verify_token.return_value = {
            'email': 'Jane@example.com',
            'email_verified': True,
            'given_name': 'Jane',
            'family_name': 'Doe',
        }

        response = self.client.post(
            reverse('google_login'),
            {'id_token': 'not-logged-or-returned'},
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.json())
        self.assertTrue(User.objects.filter(email='Jane@example.com').exists())

    def test_profile_requires_authentication(self):
        response = self.client.get(reverse('profile'))

        self.assertEqual(response.status_code, 401)

    def test_profile_only_returns_authenticated_users_own_data(self):
        user = User.objects.create_user(
            username='jane',
            email='jane@example.com',
            password='supersecret123',
        )
        self.client.force_authenticate(user=user)

        response = self.client.get(reverse('profile'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['id'], user.id)
        self.assertEqual(response.json()['email'], user.email)

    def test_public_profile_only_returns_explicitly_public_fields(self):
        user = User.objects.create_user(
            username='private@example.com',
            email='private@example.com',
            password='supersecret123',
            first_name='Jane',
            last_name='Doe',
            university='Private University',
            bio='J’apprends Python.',
        )

        response = self.client.get(reverse('public_profile', args=[user.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'id': user.id,
            'display_name': 'Jane Doe',
            'bio': 'J’apprends Python.',
            'avatar': '',
            'follower_count': 0,
            'following_count': 0,
            'is_following': False,
        })
        self.assertNotIn('email', response.json())
        self.assertNotIn('university', response.json())

    def test_authenticated_member_can_follow_and_unfollow_public_profile(self):
        follower = User.objects.create_user(
            username='follower',
            email='follower@example.com',
            password='supersecret123',
        )
        followed = User.objects.create_user(
            username='followed',
            email='followed@example.com',
            password='supersecret123',
        )
        self.client.force_authenticate(user=follower)

        follow_response = self.client.post(reverse('user_follow', args=[followed.id]))
        repeated_follow_response = self.client.post(reverse('user_follow', args=[followed.id]))
        profile_response = self.client.get(reverse('public_profile', args=[followed.id]))

        self.assertEqual(follow_response.status_code, 200)
        self.assertEqual(repeated_follow_response.status_code, 200)
        self.assertEqual(UserFollow.objects.filter(follower=follower, followed=followed).count(), 1)
        self.assertEqual(profile_response.json()['follower_count'], 1)
        self.assertTrue(profile_response.json()['is_following'])

        unfollow_response = self.client.delete(reverse('user_follow', args=[followed.id]))
        profile_response = self.client.get(reverse('public_profile', args=[followed.id]))

        self.assertEqual(unfollow_response.status_code, 200)
        self.assertEqual(profile_response.json()['follower_count'], 0)
        self.assertFalse(profile_response.json()['is_following'])

    def test_member_cannot_follow_themselves(self):
        user = User.objects.create_user(
            username='self-follow',
            email='self-follow@example.com',
            password='supersecret123',
        )
        self.client.force_authenticate(user=user)

        response = self.client.post(reverse('user_follow', args=[user.id]))

        self.assertEqual(response.status_code, 400)
        self.assertFalse(UserFollow.objects.exists())

    def test_follow_requires_authentication(self):
        followed = User.objects.create_user(
            username='public-member',
            email='public-member@example.com',
            password='supersecret123',
        )

        response = self.client.post(reverse('user_follow', args=[followed.id]))

        self.assertEqual(response.status_code, 401)
        self.assertFalse(UserFollow.objects.exists())

    def test_profile_update_accepts_a_valid_avatar(self):
        user = User.objects.create_user(
            username='jane',
            email='jane@example.com',
            password='supersecret123',
        )
        self.client.force_authenticate(user=user)
        image_data = BytesIO()
        Image.new('RGB', (8, 8), color='orange').save(image_data, format='PNG')
        image = SimpleUploadedFile('avatar.png', image_data.getvalue(), content_type='image/png')

        response = self.client.put(
            reverse('profile'),
            {'public_name': 'Jane', 'bio': 'Python learner', 'avatar': image},
            format='multipart',
        )
        user.refresh_from_db()
        self.addCleanup(lambda: user.avatar.delete(save=False) if user.avatar else None)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(user.public_name, 'Jane')
        self.assertTrue(user.avatar.name.endswith('.png'))

    def test_profile_update_rejects_non_image_avatar(self):
        user = User.objects.create_user(
            username='jane',
            email='jane@example.com',
            password='supersecret123',
        )
        self.client.force_authenticate(user=user)

        response = self.client.put(
            reverse('profile'),
            {'avatar': SimpleUploadedFile('avatar.png', b'not-an-image', content_type='image/png')},
            format='multipart',
        )

        self.assertEqual(response.status_code, 400)
        user.refresh_from_db()
        self.assertFalse(user.avatar)

    def test_inactive_user_cannot_log_in(self):
        User.objects.create_user(
            username='inactive@example.com',
            email='inactive@example.com',
            password='supersecret123',
            is_active=False,
        )

        response = self.client.post(
            reverse('accounts_token_obtain_pair'),
            {'email': 'inactive@example.com', 'password': 'supersecret123'},
            format='json',
        )

        self.assertEqual(response.status_code, 401)

    def test_login_limits_repeated_attempts(self):
        for _ in range(5):
            response = self.client.post(
                reverse('accounts_token_obtain_pair'),
                {'email': 'unknown@example.com', 'password': 'wrong-password'},
                format='json',
                REMOTE_ADDR='192.0.2.42',
            )
            self.assertEqual(response.status_code, 401)

        response = self.client.post(
            reverse('accounts_token_obtain_pair'),
            {'email': 'unknown@example.com', 'password': 'wrong-password'},
            format='json',
            REMOTE_ADDR='192.0.2.42',
        )
        self.assertEqual(response.status_code, 429)

    def test_logout_blacklists_own_refresh_token(self):
        user = User.objects.create_user(
            username='jane',
            email='jane@example.com',
            password='supersecret123',
        )
        refresh = RefreshToken.for_user(user)
        self.client.force_authenticate(user=user)

        response = self.client.post(
            reverse('logout'),
            {'refresh': str(refresh)},
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.client.force_authenticate(user=None)
        refresh_response = self.client.post(
            reverse('token_refresh'),
            {'refresh': str(refresh)},
            format='json',
        )
        self.assertEqual(refresh_response.status_code, 401)

    def test_logout_cannot_revoke_another_users_refresh_token(self):
        owner = User.objects.create_user(
            username='owner',
            email='owner@example.com',
            password='supersecret123',
        )
        other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='supersecret123',
        )
        refresh = RefreshToken.for_user(owner)
        self.client.force_authenticate(user=other_user)

        response = self.client.post(
            reverse('logout'),
            {'refresh': str(refresh)},
            format='json',
        )

        self.assertEqual(response.status_code, 403)
        self.client.force_authenticate(user=None)
        refresh_response = self.client.post(
            reverse('token_refresh'),
            {'refresh': str(refresh)},
            format='json',
        )
        self.assertEqual(refresh_response.status_code, 200)
