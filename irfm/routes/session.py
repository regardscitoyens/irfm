# -*- coding: utf-8 -*-


from flask import abort, flash, redirect, request, session, url_for

from .util import check_email, redirect_back, sanitize


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
