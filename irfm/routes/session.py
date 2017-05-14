# -*- coding: utf-8 -*-

from flask import request, session

from ..tools.routing import redirect_back
from ..tools.text import check_email, check_password, sanitize


def setup_routes(app):

    @app.route('/login', methods=['POST'])
    def login():
        if app.config['ADMIN_PASSWORD'] and request.form['nick'] == '!rc':
            if check_password(request.form['email'],
                              app.config['ADMIN_PASSWORD'],
                              app.config['SECRET_KEY']):
                session['user'] = {
                    'nick': '!rc',
                    'email': app.config['ADMIN_EMAIL'],
                    'admin': True
                }

                return redirect_back()

        nick = sanitize(request.form['nick'])

        if nick != request.form['nick']:
            msg = 'Seuls les caractères suivants sont autorisés: ' \
                  'a-z 0-9 _ - @ . '
            return redirect_back(error=msg)

        if not len(nick):
            msg = 'Veuillez saisir un pseudonyme !'
            return redirect_back(error=msg)

        if not check_email(request.form['email'].strip()):
            msg = 'Veuillez saisir une adresse e-mail valide pour assurer ' \
                  'le suivi de l\'envoi des demandes ! Vous pouvez aussi ' \
                  'laisser le champ vide si vous le préférez.'
            return redirect_back(error=msg)

        session['user'] = {
            'nick': nick,
            'email': request.form['email'].strip(),
            'admin': False
        }

        return redirect_back()

    @app.route('/logout')
    def logout():
        session.pop('user', None)

        return redirect_back()
