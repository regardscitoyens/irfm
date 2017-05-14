# -*- coding: utf-8 -*-

import re
import unicodedata
from urllib.parse import urlparse, urljoin

from flask import request


SLUG_STRIP_RE = re.compile(r'[^\w\s-]')
SLUG_HYP_RE = re.compile(r'[-\s]+')


def check_email(text, allow_empty=True):
    return not text or re.search(r'^[^@]+@[^@]+\.[^@]+$', text)


def check_suivi(text):
    return text and re.search(r'^\d[A-Z]\d{11}$', text.upper())


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc


def sanitize(text):
    return re.sub(r'[^@A-Za-z0-9_.-]', '', text)


def slugify(value):
    if not isinstance(value, str):
        value = str(value)
    value = str(unicodedata.normalize('NFKD', value).encode('ascii', 'ignore'))
    value = str(SLUG_STRIP_RE.sub('', value).strip().lower())
    value = SLUG_HYP_RE.sub('-', value)

    return value[1:]
