# -*- coding: utf-8 -*-

import re

from flask import abort, flash, redirect, request, session, url_for
from urllib.parse import urlparse, urljoin


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


def setup_routes(app):

    @app.route('/login', methods=['POST'])
    def login():
        nick = sanitize(request.form['nick'])
        if nick != request.form['nick']:
            flash('Seuls les caractères suivants sont autorisés: '
                  'a-z 0-9 _ - @ . ', category='error')
            return redirect_back()

        if not len(nick):
            flash('Veuillez saisir un pseudonyme !', category='error')
            return redirect_back()

        if not check_email(request.form['email']):
            flash('Veuillez saisir une adresse e-mail valide pour assurer le '
                  'suivi de l\'envoi des demandes !', category='error')
            return redirect_back()

        session['user'] = {
            'nick': nick,
            'email': request.form['email'],
        }

        return redirect_back()

    @app.route('/logout')
    def logout():
        session.pop('user', None)

        return redirect_back()
