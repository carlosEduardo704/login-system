from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.urls import reverse
from users.models import CustomUser

class UserTest(TestCase):
    
    def test_invalid_email_validate(self):
        user = CustomUser(
                email = 'carloscom',
                password = 'teste1234'
            )

        with self.assertRaises(ValidationError) as cm:
            user.full_clean()

        self.assertIn('email', cm.exception.message_dict)

    def test_valid_email_validate(self):
        user = CustomUser(
                email = 'carlos@gmail.com',
                password = 'teste1234'
            )

        try:
            user.full_clean()
        except ValidationError:
            self.fail("full_clean() levantou ValidationError com e-mail válido!")

