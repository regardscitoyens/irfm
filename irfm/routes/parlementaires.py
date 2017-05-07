# -*- coding: utf-8 -*-

from datetime import datetime
import os

from flask import (flash, make_response, redirect, render_template, request,
                   session, url_for)
from sqlalchemy.orm import joinedload, contains_eager

from .util import not_found, redirect_back, require_user, slugify
from ..models import db, Action, Etape, Parlementaire
from ..models.constants import ETAPE_A_ENVOYER, ETAPE_A_CONFIRMER, ETAPE_ENVOYE


EXTENSIONS = {
    'pdf': 'application/pdf',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
}


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
                ip=request.remote_addr,
                parlementaire=parl,
                etape=parl.etape
            )

            db.session.add(action)
            db.session.commit()

            return redirect(url_for('parlementaire', id=id))
        finally:
            db.session.rollback()

    @app.route('/parlementaire/<id>/annuler', endpoint='annuler')
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

    @app.route('/parlementaire/<id>/confirmer', endpoint='confirmer',
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

        if 'file' not in request.files or not request.files['file'] \
           or request.files['file'].filename == '':
            msg = 'Veuillez indiquer un fichier à envoyer'
            return redirect_back(error=msg,
                                 fallback=url_for('parlementaire', id=id))

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
        file.save(os.path.join(app.config['DATA_DIR'], filename))

        parl.etape = Etape.query.filter_by(ordre=ETAPE_ENVOYE).first()

        action = Action(
            date=datetime.utcnow(),
            nick=session['user']['nick'],
            email=session['user']['email'],
            ip=request.remote_addr,
            parlementaire=parl,
            etape=parl.etape,
            attachment=filename
        )

        db.session.add(action)
        db.session.commit()

        flash('Confirmation reçue, merci beaucoup !', category='success')
        return redirect(url_for('parlementaire', id=id))

    @app.route('/parlementaire/<id>/preuve-envoi', endpoint='preuve_envoi')
    def preuve_envoi(id):
        act = Action.query.join(Action.etape) \
                          .filter(Etape.ordre == ETAPE_ENVOYE,
                                  Action.parlementaire_id == id) \
                          .first()

        if not act or not act.attachment:
            return not_found()

        path = os.path.join(app.config['DATA_DIR'], act.attachment)
        ext = path.rsplit('.', 1)[1].lower()

        with open(path, 'rb') as preuve:
            response = make_response(preuve.read())
            response.headers['Content-Type'] = EXTENSIONS[ext]
            return response
