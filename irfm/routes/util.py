# -*- coding: utf-8 -*-

import re
import unicodedata
from urllib.parse import urlparse, urljoin

from flask import flash, redirect, request, session, url_for


SLUG_STRIP_RE = re.compile(r'[^\w\s-]')
SLUG_HYP_RE = re.compile(r'[-\s]+')


def slugify(value):
    if not isinstance(value, str):
        value = str(value)
    value = str(unicodedata.normalize('NFKD', value).encode('ascii', 'ignore'))
    value = str(SLUG_STRIP_RE.sub('', value).strip().lower())
    value = SLUG_HYP_RE.sub('-', value)

    return value[1:]


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc


def redirect_back(fallback=None, error=None):
    if error:
        flash(error, category='error')

    if request.referrer and is_safe_url(request.referrer):
        return redirect(request.referrer)
    elif fallback and is_safe_url(fallback):
        return redirect(fallback)
    else:
        return redirect(url_for('home'))


def not_found():
    return redirect_back(error='Oups, la page demandée n\'existe pas')


def sanitize(text):
    return re.sub(r'[^@A-Za-z0-9_.-]', '', text)


def check_email(text, allow_empty=True):
    return not text or re.search(r'^[^@]+@[^@]+\.[^@]+$', text)


def check_suivi(text):
    return text and re.search(r'^\d[A-Z]\d{11}$', text.upper())


def require_user(f):
    def decorator(*args, **kwargs):
        if not session.get('user'):
            return redirect_back(error='Vous devez vous identifier pour '
                                       'accéder à cette page')

        return f(*args, **kwargs)

    return decorator


def require_admin(f):
    def decorator(*args, **kwargs):
        if not session.get('user') or not session.get('user')['admin']:
            return not_found()

        return f(*args, **kwargs)

    return decorator


def remote_addr():
    return request.headers.get('X-Forwarded-For', request.remote_addr)
