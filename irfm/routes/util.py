# -*- coding: utf-8 -*-

import re
import unicodedata
from urllib.parse import urlparse, urljoin

from flask import (abort, make_response, redirect, render_template, request,
                   session)


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


def redirect_back():
    if request.referrer and is_safe_url(request.referrer):
        return redirect(request.referrer)
    else:
        return redirect(url_for('home'))


def sanitize(text):
    return re.sub(r'[^@A-Za-z0-9_.-]', '', text)


def check_email(text):
    return re.search(r'^[^@]+@[^@]+\.[^@]+$', text)


def require_user(f):
    def decorator(*args, **kwargs):
        if not session.get('user'):
            flash('Vous devez vous identifier pour accéder à cette page',
                  category='error')
            return redirect_back()

        return f(*args, **kwargs)

    return decorator
