# -*- coding: utf-8 -*-

from flask import abort, render_template
from sqlalchemy.orm import joinedload, contains_eager

from ..models import Etape, Parlementaire


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

    @app.route('/parlementaires/<id>/demande', endpoint='demande')
    def demande(id):
        parl = Parlementaire.query.filter_by(id=id).first()

        if not parl:
            abort(404)

        return render_template(
            'demande.html.j2',
            parlementaire=parl
        )
