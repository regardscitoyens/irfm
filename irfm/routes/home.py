# -*- coding: utf-8 -*-

from flask import render_template
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import func

from ..models import db, Etape, Parlementaire
from ..models.constants import ETAPE_NA, ETAPE_A_ENVOYER


def setup_routes(app):

    @app.route('/', endpoint='home')
    def home():
        pqs = Parlementaire.query.options(joinedload(Parlementaire.etape)) \
                                 .filter(Etape.ordre == ETAPE_A_ENVOYER) \
                                 .order_by(func.random())

        eqs = db.session.query(Etape) \
                        .outerjoin(Etape.parlementaires) \
                        .add_columns(func.count(Parlementaire.id)
                                         .label('nb')) \
                        .filter(Etape.ordre > ETAPE_NA) \
                        .group_by(Etape) \
                        .order_by(Etape.ordre) \
                        .all()

        return render_template(
            'index.html.j2',
            parlementaire=pqs.first(),
            etapes=[e.Etape for e in eqs],
            etapes_data={
                'labels': [e.Etape.label for e in eqs],
                'datasets': [{
                    'data': [e.nb for e in eqs],
                    'backgroundColor': [e.Etape.couleur for e in eqs]
                }]
            }
        )
