# -*- coding: utf-8 -*-

from flask import flash, request, session

from ..models import User, db

from ..tools.routing import redirect_back
from ..tools.text import check_email, check_password, sanitize_hard


def setup_routes(app):

    @app.route('/login', methods=['POST'])
    def login():
        if app.config['ADMIN_PASSWORD'] and request.form['nick'] == '!rc':
            if check_password(request.form['email'],
                              app.config['ADMIN_PASSWORD'],
                              app.config['SECRET_KEY']):

                # Ensure admin user exists and update its email
                changed = False
                admin = User.query.filter_by(admin=True).first()
                if not admin:
                    admin = User(nick='!rc', admin=True, abo_rc=False,
                                 abo_membres=False, abo_irfm=False)
                    db.session.add(admin)
                    changed = True

                if admin.email != app.config['ADMIN_EMAIL']:
                    admin.email = app.config['ADMIN_EMAIL']
                    changed = True

                if changed:
                    db.session.commit()

                session['user'] = {
                    'id': admin.id,
                    'nick': '!rc',
                    'email': app.config['ADMIN_EMAIL'],
                    'admin': True
                }

                return redirect_back()

        nick = sanitize_hard(request.form['nick'])

        if nick != request.form['nick']:
            msg = 'Seuls les caractères suivants sont autorisés: ' \
                  'a-z 0-9 _ - @ . '
            return redirect_back(error=msg)

        if not len(nick):
            msg = 'Veuillez saisir un pseudonyme !'
            return redirect_back(error=msg)

        email = request.form['email'].strip()
        if not check_email(email):
            msg = 'Veuillez saisir une adresse e-mail valide pour assurer ' \
                  'le suivi de l\'envoi des demandes !'
            return redirect_back(error=msg)

        user = User.query.filter(User.nick == nick).first()

        if user and user.email != email:
            msg = 'L\'adresse e-mail que vous avez saisie n\'est pas la bonne.'
            return redirect_back(error=msg)

        if not user:
            user = User(nick=nick, email=email, admin=False, abo_rc=False,
                        abo_membres=False, abo_irfm=False)
            db.session.add(user)
            db.session.commit()
            flash('Bienvenue %s !' % nick, category='success')

        session['user'] = {
            'id': user.id,
            'nick': nick,
            'email': email,
            'admin': False
        }

        return redirect_back()

    @app.route('/logout')
    def logout():
        session.pop('user', None)

        return redirect_back()
