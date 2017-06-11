# -*- coding: utf-8 -*-

import hmac
import re
import unicodedata
from urllib.parse import urljoin, urlparse

from flask import request


SLUG_STRIP_RE = re.compile(r'[^\w\s-]')
SLUG_HYP_RE = re.compile(r'[-\s]+')


def check_email(text):
    return re.search(r'^[^@]+@[^@]+\.[^@]+$', text)


def check_password(candidate, hashed_password, secret):
    return hmac.compare_digest(hash_password(candidate, secret),
                               hashed_password)


def create_usertoken(uid, secret):
    return '%s:%s' % (uid, hash_password('user #%s' % uid, secret))


def check_usertoken(token, secret):
    if ':' in token:
        uid, tok = token.split(':', 1)
        if hmac.compare_digest(hash_password('user #%s' % uid, secret), tok):
            return uid


def check_suivi(text):
    suivi = text.strip().replace(' ', '').upper()
    if suivi and re.search(r'^\d[A-Z]\d{11}$', suivi):
        return suivi
    else:
        return None


def hash_password(password, secret):
    h = hmac.new(bytes(secret, encoding='ascii'))
    h.update(bytes(password, encoding='utf-8'))
    return h.hexdigest()


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc


def sanitize_hard(text):
    return re.sub(r'[^@A-Za-z0-9_.-]', '', text)


def slugify(value):
    if not isinstance(value, str):
        value = str(value)
    value = str(unicodedata.normalize('NFKD', value).encode('ascii', 'ignore'))
    value = str(SLUG_STRIP_RE.sub('', value).strip().lower())
    value = SLUG_HYP_RE.sub('-', value)

    return value[1:]
