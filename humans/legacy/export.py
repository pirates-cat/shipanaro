#!/usr/bin/python
#-*- coding: utf8 -*-
from datetime import datetime, date
from functools import partial
import traceback
import psycopg2
import MySQLdb
import base64
import pickle
import pprint
import ldap
import csv
import sys
import os
import re

# -- Helpers

regex = re.compile(("([a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`"
                    "{|}~-]+)*(@|\sat\s)(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?(\.|"
                    "\sdot\s))+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)"))
dni_regex = re.compile("^[0-9]{8}[A-Z]$")
isodate_regex = re.compile("^[0-9]{4}/[0-9]{1,2}/[0-9]{1,2}$")
short_date_regex = re.compile("^[0-9]{1,2}/[0-9]{1,2}/[0-9]{2}$")
long_date_regex = re.compile("^[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}$")


def parse_date(v):
    if v == '':
        raise Exception('empty date')
    elif long_date_regex.match(v):
        dt_fmt = '%d/%m/%Y'
    elif short_date_regex.match(v):
        dt_fmt = '%d/%m/%y'
    elif isodate_regex.match(v):
        dt_fmt = '%Y/%m/%d'
    else:
        raise Exception('unknown date: %s' % v)
    result = datetime.strptime(v, dt_fmt).date()
    if result.year >= datetime.now().year:
        result = date(result.year - 100, result.month, result.day)
    return result


def clean_nid(v):
    return v.replace(' ', '').replace('-', '').upper()


def resolve_nid_type(nid):
    if nid is None:
        raise Exception('m.nid must have value')
    # Passport
    if nid.startswith('PESP'):
        return 7240
    # NIE
    if (len(nid) == 9
            or len(nid) == 10) and (nid.startswith('X') or nid.startswith('Y')
                                    or nid.startswith('Z')):
        return 7242
    # DNI
    if dni_regex.match(nid):
        return 7241
    # Unknown
    return 0


def extract_email_from(v):
    result = [
        em[0] for em in re.findall(regex, v) if not em[0].startswith('//')
    ]
    if len(result) == 0:
        return (None, False)
    return (result[0].lower(), len(result) > 0)


def is_empty(v):
    if v is None:
        return True
    if isinstance(v, list) or isinstance(v, basestring):
        return len(v) == 0
    return False


def resolve_groups(birthday):
    groups = []
    today = datetime.now().date()
    diff = today - birthday
    years = diff.days / 365.25
    if years < 30:
        groups.append('grumets')
    if years >= 18:
        groups.append('afiliats')
    return groups


# -- Connect


def connect_to_postgresql():
    conn_pg = psycopg2.connect(
        "dbname=drupaldb2 user=drupalapp password=jie1Rahd host=127.0.0.1")
    return conn_pg.cursor()


def connect_to_mysql():
    conn = MySQLdb.connect(
        db='vtigercrm510', user='root', passwd='Fiek0ci1', host='127.0.0.1')
    return conn.cursor()


def connect_to_ldap():
    l = ldap.open('flota.pirata.cat')
    l.simple_bind('cn=Manager,dc=pirata,dc=cat', 'cSmI1nOGzFinwX1')
    return l


# -- Load


def load_csv(filename):
    c = open(filename, 'rb')
    rows = csv.reader(c, delimiter=';', quotechar='"')
    return (rows, c)


def load_drupal():
    cur_pg = connect_to_postgresql()
    cur_pg.execute(
        """select name as username, mail as email, status as is_active, created as date_joined, login as last_login from users"""
    )
    return cur_pg.fetchall()


def load_ldap():
    l = connect_to_ldap()
    baseDN = "ou=afiliats,dc=pirata,dc=cat"
    searchScope = ldap.SCOPE_SUBTREE
    ldap_result_id = l.search(baseDN, searchScope)
    results = []
    while 1:
        result_type, result_data = l.result(ldap_result_id, 0)
        if (result_data == []):
            break
        elif result_type == ldap.RES_SEARCH_ENTRY:
            results.append(result_data[0])
    l.unbind_s()
    return results


# -- Updates


def update_from_csv(mig, row):
    m = Member()
    m.update_from_csv(row)
    if m.uid is None:
        raise Exception('Missing UID for user %s' % (m.email))
    if m.postal_code == '':
        raise Exception('Missing postal code for user %s' % (m.email))
    if m.contact_id in mig.contacts and m.is_active:
        raise Exception('Duplicated contact ID: %s for users %s and %s' %
                        (m.contact_id, m.email, mig.contacts[m.contact_id]))
    mig.users[m.email] = m
    mig.contacts[m.contact_id] = m.email


def update_from_mailchimp(mig, row):
    _email = row[0].lower()
    if _email not in mig.users:
        if _email not in mig.missing_emails:
            raise Exception("Unknown e-mail address %s" % email)
        email = mig.missing_emails[_email]
    else:
        email = _email
    email = email.lower()
    m = mig.users[email]
    m.email = (email, True)
    if _email not in mig.party_addresses:
        m.email = (_email, True)
    m.newsletter = email
    m.level = int(row[1])


def update_from_vtiger(cur, mig, cid):
    cur.execute("""select
				cd.contact_no, cd.firstname as first_name, cd.lastname as last_name, cd.email as email, cd.mobile as phone,
				ca.mailingcity as city, ca.mailingstreet as address, ca.mailingcountry as nationality, ca.mailingzip as postal_code,
				csb.birthday as birthday,
				csf.cf_539 as nid, e.createdtime as date_joined, csf.cf_541 as is_active, e.description as extra
			from
				vtiger_crmentity e,
				vtiger_contactdetails cd,
				vtiger_contactaddress ca,
				vtiger_contactsubdetails csb,
				vtiger_contactscf csf
			where
				e.crmid = cd.contactid
				and e.crmid = ca.contactaddressid
				and e.crmid = csb.contactsubscriptionid
				and e.crmid = csf.contactid
				and e.setype = 'Contacts'
				and cd.contact_no = '%s'
			order by e.crmid asc""" % cid)
    u = cur.fetchone()
    if u is None:
        if cid in mig.known_missing_contacts:
            return
        raise Exception("Contact '%s' does not exist in CRM" % cid)
    u = Data(u)
    _email = u[3].lower()
    if _email in mig.party_addresses:
        r, ok = extract_email_from(u[13])
        if not ok:
            # No data, record kept by legal reasons
            return
        _email = r
    if _email not in mig.users and _email in mig.missing_emails:
        email = mig.missing_emails[_email]
    else:
        email = _email
    if email not in mig.users:
        r, ok = extract_email_from(u[13])
        if ok:
            _email = [_email, email]
            email = r
    if email not in mig.users:
        if isinstance(_email, list):
            _email.append(email)
        else:
            _email = [_email, email]
        contact_id = unicode(u[0])
        email = mig.contacts[contact_id]
    m = mig.users[email]
    m.update_from_vtiger(u)
    if isinstance(_email, list):
        for v in _email:
            v = v.lower()
            if v not in mig.party_addresses:
                m.email = (v, True)
    else:
        _email = _email.lower()
        if _email not in mig.party_addresses:
            m.email = (_email, True)


def update_from_drupal(mig, u):
    _email = u[1].lower()
    if _email == '':
        return
    if _email in mig.party_addresses:
        return
    if _email not in mig.users and _email in mig.missing_emails:
        email = mig.missing_emails[_email]
    else:
        email = _email
    if email not in mig.users:
        if u[2] != 0:
            raise Exception(
                "%s is associated to no user but it has an active user in Drupal"
                % u[1])
        return
    m = mig.users[email]
    m.update_from_drupal(u)
    _email = _email.lower()
    if _email not in mig.party_addresses:
        m.email = (_email, True)


def update_from_ldap(mig, data):
    if data[0].startswith('uid='):
        _email = data[1]['mail'][0].lower().strip()
        if _email in mig.party_addresses:
            return
        if _email not in mig.users and _email in mig.missing_emails:
            email = mig.missing_emails[_email]
        else:
            email = _email
        if email not in mig.users:
            raise Exception(
                "%s is in LDAP but we cannot find it in CRM or Drupal" % email)
        m = mig.users[email]
        m.update_from_ldap(data[1])
        _email = _email.lower()
        if _email not in mig.party_addresses:
            m.email = (_email, True)


class Data:
    def __init__(self, src):
        self.src = src

    def __getitem__(self, ix):
        v = self.src[ix]
        if isinstance(v, basestring):
            return unicode(v.strip(), 'ISO-8859-1')
        return v


class Member:
    def __init__(self):
        self.password = None
        self.date_joined = None
        self.date_left = None
        self.last_login = None
        self.is_active = False
        self.newsletter = None
        self.level = 0

    def update_from_csv(m, u):
        m.uid = int(u[0])
        m.contact_id = u[1]
        if not m.contact_id.startswith('CON'):
            m.contact_id = "CON%s" % m.contact_id
        m.first_name = u[2]
        m.last_name = u[3]
        m.username = u[4]
        sex = u[5].lower()
        if sex == 'd' or sex == 'm':
            m.assigned_sex = 2
        elif sex == 'h' or sex == 'v':
            m.assigned_sex = 1
        else:
            raise Exception("invalid assigned sex '%s'" % u[5])
        m.gender = m.assigned_sex
        m.phone = u[6]
        m.phone_2 = u[7]
        m.is_active = u[8].lower() != 'baixa'
        birthday = parse_date(u[9])
        m.groups = resolve_groups(birthday)
        m.birthday = birthday.isoformat()
        m.email = u[10].lower()
        if u[11] != '':
            m.date_joined = parse_date(u[11]).isoformat()
        if u[12] != '':
            m.date_left = parse_date(u[12]).isoformat()
        m.nid = clean_nid(u[13])
        m.nid_type = resolve_nid_type(m.nid)
        m.address = u[16]
        m.postal_code = u[17]
        m.city = u[18]
        m.province = u[19]
        n = u[20]
        if n == '':
            n = 'espanyola'
        m.nationality = n
        m.notes = u[21]

    def update_from_vtiger(m, u):
        email = u[3]
        if email == 'desactivat@pirata.cat' or email == 'partit@pirata.cat':
            m.newsletter = None
            r, ok = extract_email_from(u[13])
            if not ok:
                return
            email = r
        email = email.lower()
        m.email = (email, True)
        if is_empty(m.phone):
            m.phone = u[4]
        if m.is_active:
            m.is_active = u[12] == '1'

    def update_from_drupal(m, u):
        m.username = u[0]
        is_active = u[2] != 0
        if not m.is_active and is_active:
            raise Exception(
                "%s is no longer member but it has an active user in Drupal" %
                u[1])
        else:
            m.is_active = is_active
        if m.date_joined is None:
            m.date_joined = datetime.fromtimestamp(u[3]).date().isoformat()
        m.last_login = datetime.fromtimestamp(u[4]).date().isoformat()

    def update_from_ldap(m, u):
        m.password = u['userPassword'][0].strip()
        m.username = u['uid'][0].strip()

    def __setattr__(self, ix, v):
        multiple = False
        if isinstance(v, tuple):
            multiple = v[1]
            v = v[0]
        if ix in self.__dict__:
            src = self.__dict__[ix]
            if is_empty(src):
                if isinstance(v, basestring) and src is not None:
                    src = src.encode('utf-8')
                if v == src:
                    return
            elif is_empty(v):
                return
            if multiple:
                if isinstance(src, list):
                    if v not in src:
                        self.__dict__[ix].append(v)
                    v = self.__dict__[ix]
                else:
                    if src != v:
                        v = [src, v]
        self.__dict__[ix] = v


class Migration:
    users = {}
    contacts = {}
    known_missing_contacts = ['CON9122']
    missing_emails = {
        'miguelangel.leyes@gmail.com': 'mleyesdo@wanadoo.es',
        'zopokx@gmail.com': 'zopokx@aluren.net',
        'ferran.fompi@gmail.com': 'ferran@fompi.net',
        'contact@pau.fm': 'webmaster@bytedevil.es',
        'pinger@riseup.net': 'revoluciondigital@gmail.com',
        'fontanagerard@gmail.com': 'gerardfontana@hotmail.com',
        'alexm@pirata.cat': 'alex.muntada@oliana.org',
        'pycksa@gmail.com': 'pycksa@hotmail.com',
        'lopezpiera.i@gmail.com': 'lopezpiera.i@hotmail.com',
        'fco.cervera@gmail.com': 'fco_cervera@hotmail.com',
        'miguelp@inspira.es': 'miguelp@idgl.com',
        'francesc@enphase.pro': 'francescgo@gmail.com',
        'artie.rose.black@gmail.com': 'artie_rose@hotmail.com',
        'sudobat@hipercub.com': 'sudobat@gmail.com',
        'warp3r@gmail.com': 'warp3r.lists@2shifted.com',
        'xavi@xaviervila.net': 'info@xaviervila.net',
        'sergioller+pirata@gmail.com': 'sergioller@gmail.com',
        'papapep@gmail.com': 'papapep@gmx.com',
        'elargonauta@hotmail.com': 'el.argonauta@hotmail.com',
        'moises.pirata@hotmail.com': 'emecefe@hotmail.com',
        'bruno.galdini0@gmail.com': 'bruno.galdini@bayer.com',
    }
    party_addresses = [
        'partit@pirata.cat', 'desactivat@pirata.cat', 'secretari@pirata.cat',
        'suport@pirata.cat', 'dario@pirata.cat'
    ]

    def process(self, it, rp):
        last = None
        to_close = None
        try:
            if isinstance(it, tuple):
                to_close = it[1]
                it = it[0]
            for v in it:
                last = v
                if isinstance(v, list):
                    rp(self, Data(v))
                elif isinstance(v, dict):
                    rp(self, Data(v))
                else:
                    rp(self, v)
            if to_close:
                to_close.close()
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            pprint.pprint(last)
            raise e

    def dump(self, filename):
        users = {}
        for email in self.users.keys():
            users[email] = self.users[email].__dict__
        output = open(filename, 'wb')
        pickle.dump(users, output)


m = Migration()
m.process(load_csv('base.csv'), update_from_csv)
m.process(load_csv('mailchimp.csv'), update_from_mailchimp)
m.process(m.contacts.keys(), partial(update_from_vtiger, connect_to_mysql()))
m.process(load_drupal(), update_from_drupal)
m.process(load_ldap(), update_from_ldap)
m.dump('users.pkl')
