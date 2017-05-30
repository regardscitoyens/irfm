# -*- coding: utf-8 -*-

from flask import flash, redirect, request, session, url_for

from .text import is_safe_url
from ..models import User


def redirect_back(fallback=None, **kwargs):
    for k, v in kwargs.items():
        flash(v, category=k)

    if request.referrer and is_safe_url(request.referrer) and \
       request.referrer != request.url:
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
            return redirect_back(login_error='Vous devez vous identifier pour '
                                             'accéder à cette page',
                                 login_next=request.url)

        if 'id' not in session['user']:
            session['user']['id'] = User.query \
                .filter(User.nick == session['user']['nick']) \
                .filter(User.email == session['user']['email']) \
                .one().id

        return f(*args, **kwargs)

    return decorator


def require_admin(f):
    def decorator(*args, **kwargs):
        if not session.get('user') or not session.get('user')['admin']:
            return not_found()

        if 'id' not in session['user']:
            session['user']['id'] = User.query \
                .filter(User.nick == session['user']['nick']) \
                .filter(User.email == session['user']['email']) \
                .one().id

        return f(*args, **kwargs)

    return decorator


def remote_addr():
    return request.headers.get('X-Forwarded-For', request.remote_addr)
