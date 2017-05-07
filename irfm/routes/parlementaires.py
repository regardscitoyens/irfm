# -*- coding: utf-8 -*-

from datetime import datetime

from flask import abort, flash, redirect, render_template, session, url_for
from sqlalchemy.orm import joinedload, contains_eager

from .util import redirect_back, require_user
from ..models import db, Action, Etape, Parlementaire
from ..models.constants import ETAPE_A_ENVOYER, ETAPE_A_CONFIRMER


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
                                  .first()

        if not parl:
            abort(404)

        return render_template(
            'parlementaire.html.j2',
            parlementaire=parl
        )

    @app.route('/parlementaires/<id>/envoi', endpoint='envoi')
    @require_user
    def envoi(id):

        try:
            # SELECT FOR UPDATE sur le parlementaire pour éviter une race
            # condition sur son étape courante
            parl = Parlementaire.query \
                                .filter_by(id=id) \
                                .with_for_update() \
                                .first()

            if not parl:
                abort(404)

            if parl.etape.ordre != ETAPE_A_ENVOYER:
                msg = 'Oups, la situation a changé pour ce parlementaire...'
                return redirect_back(error=msg,
                                     fallback=url_for('parlementaire', id=id))

            parl.etape = Etape.query.filter_by(ordre=ETAPE_A_CONFIRMER).first()

            action = Action(
                date=datetime.utcnow(),
                nick=session['user']['nick'],
                email=session['user']['email'],
                parlementaire=parl,
                etape=parl.etape
            )

            db.session.add(action)
            db.session.commit()

            return redirect(url_for('parlementaire', id=id))
        finally:
            db.session.rollback()