from hashers_passlib.converters import Converter
from binascii import hexlify, unhexlify
from base64 import b64encode, b64decode
from django.contrib.auth.hashers import SHA1PasswordHasher
from django.utils.encoding import force_bytes
import hashlib


class LDAPSHA1PasswordHasher(SHA1PasswordHasher):
    def encode(self, password, salt):
        assert password is not None
        assert salt and '$' not in salt
        hash = hashlib.sha1(force_bytes(password))
        hash.update(unhexlify(salt))
        digest = hash.hexdigest()
        return "%s$%s$%s" % (self.algorithm, salt, digest)


class ldap_salted_sha1(Converter):
    def from_orig(self, encoded):
        digest_salt = b64decode(encoded[6:])
        digest = str(hexlify(digest_salt[:20]), 'utf-8')
        salt = str(hexlify(digest_salt[20:]), 'utf-8')
        return 'sha1$%s$%s' % (salt, digest)

    def to_orig(self, encoded):
        salt_mark = encoded.find('$')
        digest_mark = encoded.find('$', salt_mark + 1)
        data = unhexlify(encoded[digest_mark + 1:])
        data += unhexlify(encoded[salt_mark + 1:digest_mark])
        return '{SSHA}%s' % str(b64encode(data), 'utf-8')
