# -*- coding: utf-8 -*-

from flask import flash, redirect, request, session, url_for

from .text import is_safe_url


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
