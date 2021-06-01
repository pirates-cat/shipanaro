from django.contrib.auth import authenticate, get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse

User = get_user_model()

PASSWORD = "tester"
NEW_PASSWORD = "piracyishealthy"


class PasswordTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="tester",
            email="tester@pirates.cat",
            password=PASSWORD,
        )
        # when we start testing, user has the old password
        logged_in = self.client.login(username=self.user.username, password=PASSWORD)
        # subsequent tests may have the modified password
        if not logged_in:
            logged_in = self.client.login(
                username=self.user.username, password=NEW_PASSWORD
            )

    def test_change_password(self):
        url = reverse("password_change")
        data = {
            "old_password": PASSWORD,
            "new_password1": NEW_PASSWORD,
            "new_password2": NEW_PASSWORD,
        }

        response = self.client.post(url, data=data, follow=True)

        self.assertEqual(response.status_code, 200)
        user = authenticate(username=self.user.username, password=NEW_PASSWORD)
        self.assertEqual(user.username, self.user.username)

    def test_reset_password(self):
        url = reverse("password_reset")
        data = {
            "email": self.user.email,
        }

        response = self.client.post(url, data=data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/password_reset_done.html")
        self.assertContains(
            response,
            "We've emailed you instructions for setting your password",
        )
        # verify sent email
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(
            "Heu rebut aquest correu",
            mail.outbox[0].body,
        )
        self.assertIn(
            f"http://testserver/accounts/password/reset/",
            mail.outbox[0].body,
        )
