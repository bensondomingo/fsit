from django.contrib.auth.models import User

from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework import status


# Test users
TEST_USERS = [
    {
        'username': 'user_a',
        'email': 'usera@test.com',
        'password1': 'djangotest1234',
        'password2': 'djangotest1234'
    },
    {
        'username': 'user_b',
        'email': 'userb@test.com',
        'password1': 'djangotest1234',
        'password2': 'djangotest1234'
    }
]


class ProfileEndpointTestCase(APITestCase):
    endpoint_registration = 'rest_register'

    def test_create_new_profile(self):
        """
        A new Profile object should be created and binded to a newly registered
        user.
        """

        endpoint = reverse(self.endpoint_registration)
        for user in TEST_USERS:
            resp = self.client.post(endpoint, data=user)
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
            user = User.objects.get(username=user.get('username'))
            self.assertIsNotNone(user.profile)
