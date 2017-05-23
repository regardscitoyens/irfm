# -*- coding: utf-8 -*-

import os
from datetime import datetime

from flask import (flash, redirect, render_template, request, session, url_for)

from flask_mail import Mail, Message

from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import case, func

from ..models import Action, Parlementaire, User, db
from ..models.constants import (ETAPE_A_CONFIRMER, ETAPE_A_ENVOYER,
                                ETAPE_COM_A_MODERER, ETAPE_COM_PUBLIE,
                                ETAPE_ENVOYE)
from ..tools.files import generer_demande, handle_upload
from ..tools.routing import not_found, redirect_back, remote_addr, require_user
from ..tools.text import check_suivi, slugify


def pris_en_charge(parl, force=False):
    """
    Verifie si l'user courant a pris en charge le parlementaire et qu'il est
    bien à l'étape "à confirmer".
    Renvoie l'action correspondante ou None
    """
    if session.get('user') and parl.etape == ETAPE_A_CONFIRMER:
        if force:
            action = [a for a in parl.actions
                      if a.etape == ETAPE_A_CONFIRMER]
        else:
            action = [a for a in parl.actions
                      if a.etape == ETAPE_A_CONFIRMER and
                      a.user_id == session.get('user')['id']]

        if len(action):
            return action[0]

    return None


def setup_routes(app):
    mail = Mail(app)
    files_root = os.path.join(app.config['DATA_DIR'], 'files')

    @app.route('/hasard', endpoint='hasard')
    def hasard():
        parl = Parlementaire.query \
                            .filter(Parlementaire.etape == ETAPE_A_ENVOYER) \
                            .order_by(func.random()) \
                            .first()
        if not parl:
            parl = Parlementaire.query \
                                .filter(Parlementaire.etape > ETAPE_NA) \
                                .order_by(func.random()) \
                                .first()

        return redirect(url_for('parlementaire', id=parl.id))

    @app.route('/parlementaires', endpoint='parlementaires')
    def parlementaires():
        qs = Parlementaire.query.options(joinedload(Parlementaire.groupe)) \
                                .filter(Parlementaire.etape > 0) \
                                .all()

        return render_template(
            'list.html.j2',
            parlementaires=qs
        )

    @app.route('/parlementaires/<id>', endpoint='parlementaire')
    def parlementaire(id):
        parl = Parlementaire.query \
                            .filter_by(id=id) \
                            .options(joinedload(Parlementaire.groupe)) \
                            .options(joinedload(Parlementaire.actions)
                                     .joinedload(Action.user)) \
                            .first()

        if not parl:
            return not_found()

        abonne = False
        abonne_dept = False

        if session.get('user'):
            user = User.query.filter(User.id == session['user']['id']) \
                             .options(joinedload(User.abonnements)) \
                             .first()
            abonne = parl in user.abonnements

            dept = Parlementaire.query.filter(Parlementaire.num_deptmt ==
                                              parl.num_deptmt) \
                                      .filter(Parlementaire.etape > 0) \
                                      .all()
            abonne_dept = all([p in user.abonnements for p in dept])

        data = {
            'parlementaire': parl,
            'abonne': abonne,
            'abonne_dept': abonne_dept,
            'pris_en_charge': bool(pris_en_charge(parl))
        }

        return render_template('parlementaire.html.j2', **data)

    @app.route('/parlementaires/<id>/envoi', endpoint='envoi')
    @require_user
    def envoi(id):

        try:
            # SELECT FOR UPDATE sur le parlementaire pour éviter une race
            # condition sur son étape courante
            parl = Parlementaire.query \
                                .filter_by(id=id) \
                                .with_for_update() \
                                .first()

            if not parl:
                return not_found()

            if parl.etape != ETAPE_A_ENVOYER:
                msg = 'Oups, la situation a changé pour ce parlementaire...'
                return redirect_back(error=msg,
                                     fallback=url_for('parlementaire', id=id))

            parl.etape = ETAPE_A_CONFIRMER

            action = Action(
                date=datetime.now(),
                user=User.query.filter(User.id == session['user']['id']).one(),
                ip=remote_addr(),
                parlementaire=parl,
                etape=parl.etape
            )

            db.session.add(action)
            db.session.commit()

            filename = generer_demande(parl, files_root)

            subject = 'Transparence IRFM - Envoi d\'une demande de documents'
            body = render_template('courriers/mail_prise_en_charge.txt.j2',
                                   parlementaire=parl)
            msg = Message(subject=subject, body=body,
                          sender=('Regards Citoyens',
                                  app.config['ADMIN_EMAIL']),
                          recipients=[session['user']['email']])

            with open(os.path.join(files_root, filename), 'rb') as f:
                msg.attach(filename, 'application/pdf', f.read())

            mail.send(msg)

            return redirect(url_for('parlementaire', id=id))
        finally:
            db.session.rollback()

    @app.route('/parlementaires/<id>/annuler', endpoint='annuler')
    @require_user
    def annuler(id):
        parl = Parlementaire.query.filter_by(id=id) \
                                  .options(joinedload(Parlementaire.groupe)) \
                                  .options(joinedload(Parlementaire.actions)) \
                                  .first()

        if not parl:
            return not_found()

        action = pris_en_charge(parl)
        if not action and not session['user']['admin']:
            msg = 'Oups, vous n\'avez pas pris en charge l\'envoi pour ce ' \
                  'parlementaire !'
            return redirect_back(error=msg,
                                 fallback=url_for('parlementaire', id=id))
        elif session['user']['admin']:
            action = pris_en_charge(parl, True)
            if not action:
                msg = 'Oups, action introuvable !'
                return redirect_back(error=msg,
                                     fallback=url_for('parlementaire', id=id))

        parl.etape = ETAPE_A_ENVOYER
        db.session.delete(action)
        db.session.commit()

        return redirect(url_for('parlementaire', id=id))

    @app.route('/parlementaires/<id>/confirmer', endpoint='confirmer',
               methods=['POST'])
    @require_user
    def confirmer(id):
        parl = Parlementaire.query.filter_by(id=id) \
                                  .options(joinedload(Parlementaire.groupe)) \
                                  .options(joinedload(Parlementaire.actions)) \
                                  .first()

        if not parl:
            return not_found()

        action = pris_en_charge(parl)
        if not action and not session['user']['admin']:
            msg = 'Oups, vous n\'avez pas pris en charge l\'envoi pour ce ' \
                  'parlementaire !'
            return redirect_back(error=msg,
                                 fallback=url_for('parlementaire', id=id))
        elif session['user']['admin']:
            action = pris_en_charge(parl, True)
            if not action:
                msg = 'Oups, action introuvable !'
                return redirect_back(error=msg,
                                     fallback=url_for('parlementaire', id=id))

        if not check_suivi(request.form['suivi']):
            msg = 'Veuillez indiquer un numéro de suivi valide'
            return redirect_back(error=msg,
                                 fallback=url_for('parlementaire', id=id))

        try:
            filename = handle_upload(
                os.path.join(app.config['DATA_DIR'], 'uploads'),
                'preuve-envoi-%s' % slugify(parl.nom_complet)
            )
        except Exception as e:
            return redirect_back(error=str(e),
                                 fallback=url_for('parlementaire', id=id))

        parl.etape = ETAPE_ENVOYE

        action = Action(
            date=datetime.now(),
            user=User.query.filter(User.id == session['user']['id']).one(),
            ip=remote_addr(),
            parlementaire=parl,
            etape=parl.etape,
            attachment=filename,
            suivi=request.form['suivi'].upper()
        )

        db.session.add(action)
        db.session.commit()

        flash('Confirmation reçue, merci beaucoup !', category='success')
        return redirect(url_for('parlementaire', id=id))

    @app.route('/parlementaires/<id>/interpeler', endpoint='interpeler',
               methods=['POST'])
    def interpeler(id):
        parl = Parlementaire.query.filter_by(id=id).first()

        if not parl:
            return not_found()

        if len(request.form['text'].strip()) < 10:
            msg = 'Veuillez saisir la réponse du parlementaire'
            return redirect_back(error=msg,
                                 fallback=url_for('parlementaire', id=id))

        if session.get('user') and session['user']['admin']:
            etape = ETAPE_COM_PUBLIE
        else:
            etape = ETAPE_COM_A_MODERER

        action = Action(
            date=datetime.now(),
            user=User.query.filter(User.id == session['user']['id'])
                           .one() if session.get('user') else None,
            ip=remote_addr(),
            parlementaire=parl,
            etape=etape,
            suivi=request.form['text']
        )

        db.session.add(action)
        db.session.commit()

        flash('Votre contribution a bien été enregistrée, elle sera publiée '
              'dès que nous l\'avons vérifiée. Merci !', category='success')
        return redirect(url_for('parlementaire', id=id))
