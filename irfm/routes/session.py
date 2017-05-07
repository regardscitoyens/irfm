# -*- coding: utf-8 -*-


from flask import request, session

from .util import check_email, redirect_back, sanitize


def setup_routes(app):

    @app.route('/login', methods=['POST'])
    def login():
        nick = sanitize(request.form['nick'])
        if nick != request.form['nick']:
            msg = 'Seuls les caractères suivants sont autorisés: ' \
                  'a-z 0-9 _ - @ . '
            return redirect_back(error=msg)

        if not len(nick):
            msg = 'Veuillez saisir un pseudonyme !'
            return redirect_back(error=msg)

        if not check_email(request.form['email']):
            msg = 'Veuillez saisir une adresse e-mail valide pour assurer ' \
                  'le suivi de l\'envoi des demandes !'
            return redirect_back(error=msg)

        session['user'] = {
            'nick': nick,
            'email': request.form['email']
        }

        return redirect_back()

    @app.route('/logout')
    def logout():
        session.pop('user', None)

        return redirect_back()
