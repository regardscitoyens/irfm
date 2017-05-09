# -*- coding: utf-8 -*-

from datetime import datetime
import os

from flask import (flash, make_response, redirect, render_template, request,
                   session, url_for)
from flask_mail import Mail, Message
from sqlalchemy.orm import joinedload, contains_eager

from .util import (check_suivi, not_found, redirect_back, remote_addr,
                   require_user, slugify)
from ..models import db, Action, Etape, Parlementaire
from ..models.constants import (ETAPE_A_ENVOYER, ETAPE_A_CONFIRMER,
                                ETAPE_ENVOYE, EXTENSIONS)


def pris_en_charge(parl):
    """
    Verifie si l'user courant a pris en charge le parlementaire et qu'il est
    bien à l'étape "à confirmer".
    Renvoie l'action correspondante ou None
    """
    if session.get('user') and parl.etape.ordre == ETAPE_A_CONFIRMER:
        action = [a for a in parl.actions
                  if a.etape.ordre == ETAPE_A_CONFIRMER
                  and a.nick == session.get('user')['nick']
                  and a.email == session.get('user')['email']]
        if len(action):
            return action[0]

    return None


def setup_routes(app):
    mail = Mail(app)

    @app.route('/parlementaires', endpoint='parlementaires')
    def parlementaires():
        qs = Parlementaire.query.join(Parlementaire.etape) \
                                .options(joinedload(Parlementaire.groupe)) \
                                .options(contains_eager(Parlementaire.etape)) \
                                .filter(Etape.ordre > 0) \
                                .all()

        return render_template(
            'list.html.j2',
            parlementaires=qs
        )

    @app.route('/parlementaires/<id>', endpoint='parlementaire')
    def parlementaire(id):
        parl = Parlementaire.query.filter_by(id=id) \
                                  .options(joinedload(Parlementaire.groupe)) \
                                  .options(joinedload(Parlementaire.etape)) \
                                  .options(joinedload(Parlementaire.actions)) \
                                  .first()

        if not parl:
            return not_found()

        return render_template(
            'parlementaire.html.j2',
            parlementaire=parl,
            pris_en_charge=bool(pris_en_charge(parl))
        )

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

            if parl.etape.ordre != ETAPE_A_ENVOYER:
                msg = 'Oups, la situation a changé pour ce parlementaire...'
                return redirect_back(error=msg,
                                     fallback=url_for('parlementaire', id=id))

            parl.etape = Etape.query.filter_by(ordre=ETAPE_A_CONFIRMER).first()

            action = Action(
                date=datetime.utcnow(),
                nick=session['user']['nick'],
                email=session['user']['email'],
                ip=remote_addr(),
                parlementaire=parl,
                etape=parl.etape
            )

            db.session.add(action)
            db.session.commit()

            subject = 'Transparence IRFM - Envoi d\'une demande de documents'
            body = render_template('text/mail_envoi.txt.j2',
                                   parlementaire=parl)
            msg = Message(subject=subject, body=body,
                          sender=('Regards Citoyens',
                                  app.config['ADMIN_EMAIL']),
                          recipients=[session['user']['email']])
            mail.send(msg)

            return redirect(url_for('parlementaire', id=id))
        finally:
            db.session.rollback()

    @app.route('/parlementaires/<id>/annuler', endpoint='annuler')
    @require_user
    def annuler(id):
        parl = Parlementaire.query.filter_by(id=id) \
                                  .options(joinedload(Parlementaire.groupe)) \
                                  .options(joinedload(Parlementaire.etape)) \
                                  .options(joinedload(Parlementaire.actions)) \
                                  .first()

        if not parl:
            return not_found()

        action = pris_en_charge(parl)
        if not action:
            msg = 'Oups, vous n\'avez pas pris en charge l\'envoi pour ce ' \
                  'parlementaire !'
            return redirect_back(error=msg,
                                 fallback=url_for('parlementaire', id=id))

        parl.etape = Etape.query.filter_by(ordre=ETAPE_A_ENVOYER).first()
        db.session.delete(action)
        db.session.commit()

        return redirect(url_for('parlementaire', id=id))

    @app.route('/parlementaires/<id>/confirmer', endpoint='confirmer',
               methods=['POST'])
    @require_user
    def confirmer(id):
        parl = Parlementaire.query.filter_by(id=id) \
                                  .options(joinedload(Parlementaire.groupe)) \
                                  .options(joinedload(Parlementaire.etape)) \
                                  .options(joinedload(Parlementaire.actions)) \
                                  .first()

        if not parl:
            return not_found()

        action = pris_en_charge(parl)
        if not action:
            msg = 'Oups, vous n\'avez pas pris en charge l\'envoi pour ce ' \
                  'parlementaire !'
            return redirect_back(error=msg,
                                 fallback=url_for('parlementaire', id=id))

        if not check_suivi(request.form['suivi']):
            msg = 'Veuillez indiquer un numéro de suivi valide'
            return redirect_back(error=msg,
                                 fallback=url_for('parlementaire', id=id))

        filename = None
        if request.files.get('file') and request.files['file'].filename != '':
            file = request.files['file']
            ext = file.filename.rsplit('.', 1)[1].lower()

            if ext not in EXTENSIONS.keys():
                msg = 'Type de fichier non pris en charge, merci d\'envoyer ' \
                      'uniquement un fichier PDF, JPG ou PNG'
                return redirect_back(error=msg,
                                     fallback=url_for('parlementaire', id=id))

            if ext == 'jpeg':
                ext = 'jpg'

            filename = 'preuve-envoi-%s.%s' % (slugify(parl.nom_complet), ext)

            uploads_root = os.path.join(app.config['DATA_DIR'], 'uploads')
            file.save(os.path.join(uploads_root, filename))

        parl.etape = Etape.query.filter_by(ordre=ETAPE_ENVOYE).first()

        action = Action(
            date=datetime.utcnow(),
            nick=session['user']['nick'],
            email=session['user']['email'],
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
