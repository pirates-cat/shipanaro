from datetime import datetime
from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.hashers import (UNUSABLE_PASSWORD_PREFIX,
                                         UNUSABLE_PASSWORD_SUFFIX_LENGTH)
from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string
from hashers_passlib.converters import ldap_sha1, ldap_md5
from shipanaro.auth.hashers import ldap_salted_sha1
from shipanaro.models import Membership, Subscription
import pickle
import pytz

User = get_user_model()


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
                if key.startswith('is_') or key == 'drop_out':
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
    pwc = PasswordConverter()

    def add_arguments(self, parser):
        parser.add_argument('file', nargs=1)

    def handle(self, *args, **options):
        filename = options['file'][0]
        f = open(filename, 'rb')
        # Latin1 encoding used because this command was developed to import
        # from an old system with Python 2.5 (no typo, 2.5).
        # Although strings were exported as Unicode (you know, u'blahblah'),
        # I guess we are dealing with THE PAST.
        users = pickle.load(f, encoding='latin1')
        try:
            src = None
            with transaction.atomic():
                for email in users:
                    src = users[email].copy()
                    m, remaining = self.__load_membership(users[email])
                    u, remaining = self.__load_user(remaining)
                    s, remaining = self.__load_subscription(remaining)
                    self.__save(u, m, s)
                    remaining = self.__save_groups(u, remaining)
                    if len(remaining) > 0:
                        raise Exception("Unassigned attributes: %s" %
                                        ', '.join(remaining.keys()))
        except Exception as e:
            if src:
                import pprint
                pprint.pprint(src)
                raise e

    def __load_membership(self, data):
        m = Porygon(Membership())
        data = m.morph(data)
        mp = m.payload
        if mp.date_left:
            mp.date_left = pytz.utc.localize(
                datetime.strptime(mp.date_left, '%Y-%m-%d'))
            mp.drop_out = True
        mp.birthday = pytz.utc.localize(
            datetime.strptime(mp.birthday, '%Y-%m-%d'))
        return (mp, data)

    def __load_user(self, data):
        u = Porygon(User())
        data = u.morph(data)
        up = u.payload
        if isinstance(up.email, list):
            up.email = up.email[0]
        up.username = up.username.encode('latin-1')
        up.password = self.pwc.convert(up.password)
        up.date_joined = pytz.utc.localize(
            datetime.strptime(up.date_joined, '%Y-%m-%d'))
        if up.last_login:
            up.last_login = pytz.utc.localize(
                datetime.strptime(up.last_login, '%Y-%m-%d'))
        return (up, data)

    def __load_subscription(self, data):
        s = None
        if 'newsletter' in data:
            email = data['newsletter']
            if email:
                s = Subscription()
                s.service = 'newsletter'
                s.endpoint = email
            del data['newsletter']
        return (s, data)

    def __save(self, user, membership, subscription):
        user.save()
        membership.user = user
        membership.save()
        if subscription:
            subscription.member = membership
            subscription.save()

    def __save_groups(self, user, data):
        if 'groups' in data:
            for gid in data['groups']:
                g = Group.objects.get(name=gid)
                g.user_set.add(user)
            del data['groups']
        return data
