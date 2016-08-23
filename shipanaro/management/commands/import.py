from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth.hashers import (
    UNUSABLE_PASSWORD_PREFIX, UNUSABLE_PASSWORD_SUFFIX_LENGTH
)
from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string
from hashers_passlib.converters import ldap_sha1, ldap_md5
from shipanaro.hashers import ldap_salted_sha1
from shipanaro.models import Membership, Subscription
import pickle


class Porygon:
    payload = None

    def __init__(self, payload):
        self.payload = payload

    def morph(self, data):
        for key in self.payload.__dict__.keys():
            if self.__blacklisted(key) and key not in data:
                continue
            try:
                setattr(self.payload, key, data[key])
            except KeyError as e:
                if key.startswith('is_'):
                    setattr(self.payload, key, False)
                else:
                    raise e
            if key in data:
                del data[key]
        return data

    def __blacklisted(self, key):
        if key.startswith('_'):
            return True
        elif key == 'id' or key.endswith('_id'):
            return True
        return False


class PasswordConverter:

    def __init__(self):
        self.ssha1 = ldap_salted_sha1()
        self.sha1 = ldap_sha1()
        self.md5 = ldap_md5()

    def convert(self, password):
        if password is None or password == '':
            return UNUSABLE_PASSWORD_PREFIX + get_random_string(
                UNUSABLE_PASSWORD_SUFFIX_LENGTH)
        result = None
        if password.startswith('{SSHA'):
            result = self.ssha1.from_orig(password)
        elif password.startswith('{SHA'):
            result = self.sha1.from_orig(password)
        elif password.startswith('{MD5'):
            result = "md5$$%s" % self.md5.from_orig(password)
        if result:
            return result
        raise Exception("Invalid password: '%s'" % (password))


class Command(BaseCommand):
    help = 'Imports pickled users map from file'

    def add_arguments(self, parser):
        parser.add_argument('file', nargs=1)

    def handle(self, *args, **options):
        filename = options['file'][0]
        f = open(filename, 'rb')
        pwc = PasswordConverter()
        # Latin1 encoding used because this command was developed to import
        # from an old system with Python 2.5 (no typo, 2.5).
        # Although strings were exported as Unicode (you know, u'blahblah'),
        # I guess we are dealing with THE PAST.
        users = pickle.load(f, encoding='latin1')
        src = None
        try:
            with transaction.atomic():
                for email in users:
                    src = users[email].copy()
                    m = Porygon(Membership())
                    remaining = m.morph(users[email])
                    u = Porygon(User())
                    remaining = u.morph(remaining)
                    u.payload.password = pwc.convert(u.payload.password)
                    s = None
                    if 'newsletter' in remaining:
                        s = Subscription()
                        s.service = 'newsletter'
                        if isinstance(u.payload.email, list):
                            s.endpoint = u.payload.email[1]
                        else:
                            s.endpoint = u.payload.email
                        del remaining['newsletter']
                    if len(remaining) > 0:
                        raise Exception("Unassigned attributes: %s" % ', '.join(
                            remaining.keys()))
                    if isinstance(u.payload.email, list):
                        if len(u.payload.email) > 2:
                            raise Exception("Too much e-mails!")
                        u.payload.email = u.payload.email[0]
                    u.payload.save()
                    m.payload.user = u.payload
                    m.payload.save()
                    if s:
                        s.member = m.payload
                        s.save()
        except Exception as e:
            if src:
                import pprint
                pprint.pprint(src)
                raise e
