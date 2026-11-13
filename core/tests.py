from django.urls import reverse
from rest_framework.test import APITestCase

from .models import ContactMessage


class ContactAPITests(APITestCase):
    def test_public_contact_message_is_saved(self):
        response = self.client.post(
            reverse('contact'),
            {
                'name': 'Test User',
                'email': 'test@example.com',
                'subject': 'Question',
                'message': 'Bonjour',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(ContactMessage.objects.count(), 1)
