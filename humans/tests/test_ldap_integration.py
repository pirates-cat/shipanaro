from random import randint

from django.contrib.auth import authenticate, get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from humans.directory import Directory

User = get_user_model()

PASSWORD = "tester"
NEW_PASSWORD = "piracyishealthy"


class LDAPIntegrationTest(TestCase):

    def setUp(self):
        super().setUp()
        self.directory = Directory()

    def create_user(self, auto_cleanup=True):
        name = f"tester-{randint(0, 10000)}"
        self.user = User(
            username=name,
            email=f"{name}@pirates.cat",
            first_name=name,
            last_name="Pirata",
        )
        self.user.save()
        if auto_cleanup:
            self.addCleanup(self.deleteLeftoverUser)
        return self.user

    def deleteLeftoverUser(self):
        if self.user.id:
            self.user.delete()

    def test_new_user_is_created_in_ldap_with_no_password(self):
        user = self.create_user()

        uid, attrs = self.directory.get_user(user.username)

        self.assertEquals(uid, f"uid={user.username},ou=afiliats,dc=pirata,dc=cat")
        self.assertEquals(attrs["cn"][0].decode(), user.username)
        self.assertNotIn("userPassword", attrs.keys())

    def test_save_password_sets_password_in_ldap(self):
        user = self.create_user()
        user.set_password(PASSWORD)
        user.save()

        _, attrs = self.directory.get_user(user.username)

        self.assertEquals(attrs["cn"][0].decode(), user.username)
        self.assertEquals(attrs["userPassword"][0].decode()[0:6], "{SSHA}")

    def test_deleted_user_is_removed_from_ldap(self):
        user = self.create_user(auto_cleanup=False)
        user.delete()

        _, attrs = self.directory.get_user(user.username)

        self.assertIsNone(attrs)

    def test_deactivated_user_is_removed_from_ldap(self):
        user = self.create_user(auto_cleanup=False)
        user.is_active = False
        user.save()

        _, attrs = self.directory.get_user(user.username)

        self.assertIsNone(attrs)

    def test_reactivated_user_is_created_in_ldap(self):
        user = self.create_user()
        user.is_active = False
        user.save()

        user.is_active = True
        user.save()

        _, attrs = self.directory.get_user(user.username)

        self.assertEquals(attrs["cn"][0].decode(), user.username)
