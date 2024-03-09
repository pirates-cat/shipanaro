from random import randint

from django.contrib.auth import authenticate, get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

User = get_user_model()

PASSWORD = "tester"
NEW_PASSWORD = "piracyishealthy"


class AuthenticationTest(TestCase):

    def setUp(self):
        super().setUp()
        name = f"tester-{randint(0, 10000)}"
        self.user = User(
            username=name,
            email=f"{name}@pirates.cat",
        )
        self.user.save()

        # set manually to active for test purposes, so they can reset password
        self.user.is_active = True
        self.user.save()

    def tearDown(self):
        if self.user.id:
            self.user.delete()

    def login(self, password):
        return self.client.login(username=self.user.username, password=password)

    def test_new_user_cannot_login(self):
        logged_in = self.login(PASSWORD)
        self.assertFalse(logged_in, "New user shouldn't be able to log in")

    def test_save_password_makes_user_able_to_login(self):
        self.user.set_password(PASSWORD)
        self.user.save()
        logged_in = self.login(PASSWORD)

        self.assertTrue(
            logged_in, "After setting password, user should be able to log in"
        )

    def test_logged_in_user_can_change_password(self):
        # set a password first to ensure we can log in
        self.user.set_password(PASSWORD)
        self.user.save()
        self.login(PASSWORD)

        response = self.client.post(
            reverse("password_change"),
            data={
                "old_password": PASSWORD,
                "new_password1": NEW_PASSWORD,
                "new_password2": NEW_PASSWORD,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        user = authenticate(username=self.user.username, password=NEW_PASSWORD)
        self.assertEqual(user.username, self.user.username)

        self.assertTrue(self.login(NEW_PASSWORD))

    def test_reset_password_process_sends_email(self):
        response = self.client.post(
            reverse("password_reset"),
            data={
                "email": self.user.email,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/password_reset_done.html")

        # verify sent email
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(
            "Rebs aquest correu",
            mail.outbox[0].body,
        )
        self.assertIn(
            f"http://testserver/accounts/password/reset/",
            mail.outbox[0].body,
        )

    def test_deleted_user_no_cannot_log_in(self):
        # set a password first to ensure we have a user in LDAP that can log in
        self.user.set_password(PASSWORD)
        self.user.save()
        self.user.delete()

        logged_in = self.login(PASSWORD)
        self.assertFalse(logged_in, "New user shouldn't be able to log in")
