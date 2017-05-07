# -*- coding: utf-8 -*-

from flask import render_template
from sqlalchemy.orm import contains_eager, joinedload

from .util import redirect_back, require_admin
from ..models import db, Action, Etape, Parlementaire
from ..models.constants import ETAPE_A_ENVOYER, ETAPE_A_CONFIRMER


def setup_routes(app):

    @app.route('/admin/recent', endpoint='admin_recent')
    @require_admin
    def admin_recent():
        qs = Action.query.options(joinedload(Action.parlementaire)) \
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
        parls = db.session.query(Parlementaire.id) \
                          .join(Parlementaire.etape) \
                          .filter(Etape.ordre == ETAPE_A_CONFIRMER) \
                          .subquery()

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
