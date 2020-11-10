from django.test import TestCase
from humans.auth.hashers import ldap_salted_sha1, LDAPSHA1PasswordHasher
from hashers_passlib.converters import ldap_md5, ldap_sha1
from django.contrib.auth.hashers import UnsaltedMD5PasswordHasher
from django.contrib.auth.hashers import UnsaltedSHA1PasswordHasher


class LDAPTestCase(TestCase):

    plain_password = 'shipanaro'
    plain_salt = '6feaaddf'

    expected_ssha1 = '{SSHA}CPp+6Tj1Unt+y65S2SGqinbH7aVv6q3f'
    expected_md5 = '{MD5}fVBMnEWjFHzasMbd0VFwvQ=='
    expected_sha1 = '{SHA}d7CnlPy0RjGBuUDWbWhwvdLQAAI='

    def testSSHA1(self):
        c = ldap_salted_sha1()
        ssha1_encoded = c.from_orig(self.expected_ssha1)
        h = LDAPSHA1PasswordHasher()
        django_ssha1_encoded = h.encode(self.plain_password, self.plain_salt)
        assert ssha1_encoded == django_ssha1_encoded
        assert self.expected_ssha1 == c.to_orig(ssha1_encoded)
        assert h.verify(self.plain_password, ssha1_encoded)

    def testMD5(self):
        c = ldap_md5()
        md5_encoded = c.from_orig(self.expected_md5)
        h = UnsaltedMD5PasswordHasher()
        django_md5_encoded = h.encode(self.plain_password, '')
        assert md5_encoded == django_md5_encoded
        assert self.expected_md5 == c.to_orig(md5_encoded)

    def testSHA1(self):
        c = ldap_sha1()
        sha1_encoded = c.from_orig(self.expected_sha1)
        h = UnsaltedSHA1PasswordHasher()
        django_sha1_encoded = h.encode(self.plain_password, '')
        assert sha1_encoded == django_sha1_encoded
        assert self.expected_sha1 == c.to_orig(sha1_encoded)
