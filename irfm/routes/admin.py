# -*- coding: utf-8 -*-

import os
from datetime import datetime

from flask import (make_response, redirect, render_template, request, session,
                   url_for)
from sqlalchemy.orm import joinedload

from ..models import Action, Etape, Parlementaire, User, db
from ..models.constants import (ETAPE_A_CONFIRMER, ETAPE_A_ENVOYER,
                                ETAPE_COM_A_MODERER, ETAPE_COM_PUBLIE)

from ..tools.files import EXTENSIONS, handle_upload
from ..tools.routing import (not_found, redirect_back, remote_addr,
                             require_admin)
from ..tools.text import slugify


def setup_routes(app):

    @app.route('/admin/recent', endpoint='admin_recent')
    @require_admin
    def admin_recent():
        # Les 500 actions les plus récentes
        qs = Action.query.options(joinedload(Action.parlementaire)
                                  .joinedload(Parlementaire.etape)) \
                         .options(joinedload(Action.etape)) \
                         .options(joinedload(Action.user)) \
                         .order_by(Action.date.desc()) \
                         .limit(500) \
                         .all()

        return render_template('admin_recent.html.j2',
                               titre='Actions récentes',
                               actions=qs)

    @app.route('/admin/en-attente', endpoint='admin_en_attente')
    @require_admin
    def admin_en_attente():
        # Sous requête des parlementaires à l'étape "à confirmer"
        parls = db.session.query(Parlementaire.id) \
                          .join(Parlementaire.etape) \
                          .filter(Etape.ordre == ETAPE_A_CONFIRMER) \
                          .subquery()

        # Actions "à confirmer" pour ces parlementaires
        qs = Action.query.join(Action.etape) \
                         .filter(Action.parlementaire_id.in_(parls)) \
                         .filter(Etape.ordre == ETAPE_A_CONFIRMER) \
                         .options(joinedload(Action.user)) \
                         .order_by(Action.date) \
                         .all()

        return render_template('admin_recent.html.j2',
                               titre='Actions en attente',
                               actions=qs)

    @app.route('/admin/commentaires', endpoint='admin_commentaires')
    @require_admin
    def admin_commentaires():
        qs = Action.query.join(Action.etape) \
                         .filter(Etape.ordre == ETAPE_COM_A_MODERER) \
                         .options(joinedload(Action.parlementaire)) \
                         .options(joinedload(Action.user)) \
                         .order_by(Action.date) \
                         .all()

        return render_template('admin_commentaires.html.j2', actions=qs)

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

            if last_action and last_action.etape.ordre > ETAPE_A_ENVOYER:
                etape = last_action.etape
            else:
                etape = Etape.query.filter_by(ordre=ETAPE_A_ENVOYER).first()

            parl = Parlementaire.query.filter_by(id=parl_id).first()
            parl.etape = etape

            db.session.commit()

        return redirect_back()

    @app.route('/admin/publish/<id>', endpoint='admin_publish')
    @require_admin
    def admin_publish(id):
        action = Action.query \
                       .join(Action.etape) \
                       .filter(Etape.ordre == ETAPE_COM_A_MODERER) \
                       .filter(Action.id == id) \
                       .first()

        if action:
            action.etape = Etape.query \
                                .filter(Etape.ordre == ETAPE_COM_PUBLIE) \
                                .one()
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

    @app.route('/admin/action/<id_parl>', endpoint='admin_action',
               methods=['POST'])
    @require_admin
    def admin_action(id_parl):
        parl = Parlementaire.query.filter_by(id=id_parl).first()
        if not parl:
            return not_found()

        etape = Etape.query.filter_by(id=request.form['etape']).first()
        if not etape:
            msg = 'Etape inconnue !?'
            return redirect_back(error=msg,
                                 fallback=url_for('parlementaire', id=id_parl))

        try:
            filename = handle_upload(
                os.path.join(app.config['DATA_DIR'], 'uploads'),
                'etape-%s-%s' % (etape.ordre, slugify(parl.nom_complet))
            )
        except Exception as e:
            return redirect_back(error=str(e),
                                 fallback=url_for('parlementaire', id=id_parl))

        parl.etape = etape

        action = Action(
            date=datetime.now(),
            user=User.query.filter(User.id == session['user']['id']).one(),
            ip=remote_addr(),
            parlementaire=parl,
            etape=etape,
            attachment=filename,
            suivi=request.form['suivi']
        )

        db.session.add(action)
        db.session.commit()

        return redirect(url_for('parlementaire', id=id_parl))
