# -*- coding: utf-8 -*-

from flask import flash, redirect, render_template, request, session, url_for

from sqlalchemy.orm import joinedload

from ..models import Action, Parlementaire, User, db
from ..models.constants import ETAPE_A_CONFIRMER, ETAPE_ENVOYE

from ..tools.routing import not_found, redirect_back, require_user
from ..tools.text import (check_email, check_password, is_safe_url,
                          sanitize_hard)


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
            return redirect_back(login_error=msg)

        if not len(nick):
            msg = 'Veuillez saisir un pseudonyme !'
            return redirect_back(login_error=msg)

        email = request.form['email'].strip()
        if not check_email(email):
            msg = 'Veuillez saisir une adresse e-mail valide pour assurer ' \
                  'le suivi de l\'envoi des demandes !'
            return redirect_back(login_error=msg)

        user = User.query.filter(User.nick == nick).first()

        if user and user.email != email:
            msg = 'L\'adresse e-mail que vous avez saisie n\'est pas la bonne.'
            return redirect_back(login_error=msg)

        if not user:
            user = User(nick=nick, email=email, admin=False)
            db.session.add(user)
            db.session.commit()
            flash('Bienvenue %s ! Vous pouvez gérer vos abonnements et vos '
                  'alertes en cliquant sur votre pseudo en haut à droite de '
                  'cette page.' % nick, category='success')

        session['user'] = {
            'id': user.id,
            'nick': nick,
            'email': email,
            'admin': False
        }

        if 'prendre_en_charge' in request.form:
            return redirect(url_for('envoi',
                                    id=request.form['prendre_en_charge']))

        if 'next' in request.form and is_safe_url(request.form['next']):
            return redirect(request.form['next'])

        return redirect_back()

    @app.route('/logout')
    def logout():
        session.pop('user', None)
        return redirect(url_for('home'))

    @app.route('/profil', endpoint='profil', methods=['GET', 'POST'])
    @require_user
    def profil():
        user = User.query.filter(User.id == session['user']['id']) \
                         .options(joinedload(User.abonnements)) \
                         .first()
        if not user:
            return not_found()

        envois = Action.query.filter(Action.user == user) \
                             .filter(Action.etape == ETAPE_ENVOYE) \
                             .count()

        if request.method == 'POST':
            changed = False
            for field in ['abo_rc', 'abo_irfm', 'abo_membres']:
                val = request.form.get(field) == field
                if getattr(user, field) != val:
                    changed = True
                    setattr(user, field, val)

            if changed:
                db.session.commit()
                flash('Vos préférences ont bien été modifiées.',
                      category='success')

            return redirect_back()

        return render_template('profil.html.j2', user=user, envois=envois)

    @app.route('/mes-actions', endpoint='mes_actions')
    @require_user
    def mes_actions():
        user = User.query.filter(User.id == session['user']['id']) \
                         .options(joinedload(User.abonnements)) \
                         .first()
        if not user:
            return not_found()

        acts = Action.query \
                     .filter(Parlementaire.id == Action.parlementaire_id) \
                     .filter(Action.etape.in_([ETAPE_ENVOYE,
                                               ETAPE_A_CONFIRMER])) \
                     .filter(Action.user_id == session['user']['id']) \
                     .exists()

        qs = Parlementaire.query.filter(acts) \
                                .options(joinedload(Parlementaire.groupe)) \
                                .order_by(Parlementaire.nom) \
                                .all()

        return render_template(
            'list.html.j2',
            parlementaires=qs,
            full_list=False
        )
