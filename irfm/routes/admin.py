# -*- coding: utf-8 -*-

import os

from flask import make_response, render_template
from sqlalchemy.orm import joinedload

from .util import not_found, redirect_back, require_admin
from ..models import db, Action, Etape, Parlementaire
from ..models.constants import ETAPE_A_ENVOYER, ETAPE_A_CONFIRMER, EXTENSIONS


def setup_routes(app):

    @app.route('/admin/recent', endpoint='admin_recent')
    @require_admin
    def admin_recent():
        # Les 500 actions les plus récentes
        qs = Action.query.options(joinedload(Action.parlementaire)
                                  .joinedload(Parlementaire.etape)) \
                         .options(joinedload(Action.etape)) \
                         .order_by(Action.date.desc()) \
                         .limit(500) \
                         .all()

        return render_template('admin_recent.html.j2',
                               titre='Actions récentes',
                               actions=qs)

    @app.route('/admin/en-attente', endpoint='admin_en_attente')
    @require_admin
    def admin_en_attente():
        # Sous requête des parlementaires à l'étape "à confirmer"
        parls = db.session.query(Parlementaire.id) \
                          .join(Parlementaire.etape) \
                          .filter(Etape.ordre == ETAPE_A_CONFIRMER) \
                          .subquery()

        # Actions "à confirmer" pour ces parlementaires
        qs = Action.query.join(Action.etape) \
                         .filter(Action.parlementaire_id.in_(parls)) \
                         .filter(Etape.ordre == ETAPE_A_CONFIRMER) \
                         .order_by(Action.date) \
                         .all()

        return render_template('admin_recent.html.j2',
                               titre='Actions en attente',
                               actions=qs)

    @app.route('/admin/delete/<id>', endpoint='admin_delete')
    @require_admin
    def admin_delete(id):
        action = Action.query.filter_by(id=id).first()

        if action:
            parl_id = action.parlementaire_id

            db.session.delete(action)
            db.session.flush()

            last_action = Action.query \
                                .join(Action.etape) \
                                .filter(Action.parlementaire_id == parl_id) \
                                .order_by(Etape.ordre.desc()) \
                                .first()

            if last_action:
                etape = last_action.etape
            else:
                etape = Etape.query.filter_by(ordre=ETAPE_A_ENVOYER).first()

            parl = Parlementaire.query.filter_by(id=parl_id).first()
            parl.etape = etape

            db.session.commit()

        return redirect_back()

    @app.route('/admin/fichier/<id_action>', endpoint='admin_fichier')
    @require_admin
    def admin_fichier(id_action):
        act = Action.query.filter_by(id=id_action).first()

        if not act or not act.attachment:
            return not_found()

        path = os.path.join(app.config['DATA_DIR'], act.attachment)
        ext = path.rsplit('.', 1)[1].lower()

        with open(path, 'rb') as fichier:
            response = make_response(fichier.read())
            response.headers['Content-Type'] = EXTENSIONS[ext]
            return response
