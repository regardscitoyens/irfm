# -*- coding: utf-8 -*-

from random import SystemRandom

from flask import flash, redirect, request, session, url_for

from ..models import Parlementaire, User, db

from ..tools.routing import not_found, redirect_back, require_user
from ..tools.text import check_email


def random_chars(length=10):
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789'

    rnd = SystemRandom()
    return ''.join([chars[rnd.randint(1, len(chars)) - 1]
                    for i in range(1, length)])


def setup_routes(app):

    @app.route('/abonnement/parlementaire/<id>/<action>',
               endpoint='abo_parlementaire')
    @require_user
    def abo_parlementaire(id, action):
        user = User.query.filter(User.id == session['user']['id']).first()
        parl = Parlementaire.query.filter(Parlementaire.id == id).first()

        if not user or not parl:
            return not_found()

        if action == 'on':
            user.abonnements.append(parl)
        else:
            user.abonnements.remove(parl)

        db.session.commit()

        return redirect_back(fallback=url_for('parlementaire', id=id))

    @app.route('/abonnement/departement/<deptmt>/<action>',
               endpoint='abo_departement')
    @require_user
    def abo_departement(deptmt, action):
        user = User.query.filter(User.id == session['user']['id']).first()
        parl = Parlementaire.query.filter(Parlementaire.num_deptmt == deptmt) \
                                  .filter(Parlementaire.etape > 0) \
                                  .all()

        if not user:
            return not_found()

        if action == 'on':
            [user.abonnements.append(p) for p in parl]
        else:
            [user.abonnements.remove(p) for p in parl]

        db.session.commit()

        return redirect_back(fallback=url_for('parlementaire', id=id))

    @app.route('/abonnement/clear')
    @require_user
    def abo_clear():
        user = User.query.filter(User.id == session['user']['id']).first()
        user.abonnements.clear()
        db.session.commit()

        return redirect_back()

    @app.route('/abonnement/anonyme', endpoint='abo_anon', methods=['POST'])
    def abo_anon():
        # Vérification e-mail
        email = request.form['email'].strip()
        if not check_email(email):
            msg = 'Veuillez saisir une adresse e-mail valide !'
            return redirect_back(error=msg)

        # Recherche user anonyme existant ou création
        user = User.query.filter(User.email == email) \
                         .filter(User.nick.like('anonyme!%')) \
                         .first()
        if not user:
            nick = None
            while not nick or User.query.filter(User.nick == nick).first():
                nick = 'anonyme!%s' % random_chars()

            user = User(nick=nick, email=email)
            db.session.add(user)

        target = request.form['abonnement']
        if target.startswith('parl-'):
            parl = Parlementaire.query \
                                .filter(Parlementaire.id == target[5:]) \
                                .first()
            if not parl:
                return not_found()

            target_str = parl.nom_complet
            parls = [parl]
        elif target.startswith('dept-'):
            dept = target[5:]
            parls = Parlementaire.query \
                                 .filter(Parlementaire.num_deptmt == dept) \
                                 .filter(Parlementaire.etape > 0) \
                                 .all()
            if not parls:
                return not_found()
            target_str = 'les parlementaires de ce département'
        else:
            return not_found()

        [user.abonnements.append(p) for p in parls]
        db.session.commit()

        flash('Vous recevrez désormais les alertes pour %s.' % target_str,
              category='success')
        return redirect_back(fallback=url_for('parlementaire', id=id))

    @app.route('/desabonnement/<anon_id>/<id>', endpoint='desabo_anon_parl')
    def desabo_anon_parl(id, anon_id):
        user = User.query.filter(User.nick == 'anonyme!%s' % anon_id).first()
        parl = Parlementaire.query.filter(Parlementaire.id == id).first()

        if not user or not parl:
            return not_found()

        if parl not in user.abonnements:
            msg = 'Vous n\'êtes pas abonné aux alertes'
        else:
            msg = 'Vous ne recevrez plus d\'alerte'
            user.abonnements.remove(parl)
            db.session.commit()

        flash('%s concernant %s' % (msg, parl.nom_complet), category='success')
        return redirect(url_for('home'))

    @app.route('/desabonnement/<anon_id>', endpoint='desabo_anon_all')
    def desabo_anon_all(anon_id):
        user = User.query.filter(User.nick == 'anonyme!%s' % anon_id).first()

        if not user:
            msg = 'Vous n\'êtes abonné à aucune alerte !'
        else:
            msg = 'Vous ne recevrez plus d\'alerte de notre part.'
            db.session.delete(user)
            db.session.commit()

        flash(msg, category='success')
        return redirect(url_for('home'))
