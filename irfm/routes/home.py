# -*- coding: utf-8 -*-

from flask import render_template
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import func

from ..models import db, Etape, Parlementaire
from ..models.constants import ETAPE_NA, ETAPE_A_ENVOYER


def setup_routes(app):

    @app.route('/', endpoint='home')
    def home():
        parl = Parlementaire.query.join(Parlementaire.etape) \
                                  .filter(Etape.ordre == ETAPE_A_ENVOYER) \
                                  .order_by(func.random()) \
                                  .first()

        etapes_qs = db.session.query(Etape) \
                              .outerjoin(Etape.parlementaires) \
                              .add_columns(func.count(Parlementaire.id)
                                               .label('nb')) \
                              .filter(Etape.ordre > ETAPE_NA) \
                              .group_by(Etape) \
                              .order_by(Etape.ordre) \
                              .all()

        return render_template(
            'index.html.j2',
            parlementaire=parl,
            etapes=[e.Etape for e in etapes_qs],
            etapes_data={
                'labels': [e.Etape.label for e in etapes_qs],
                'datasets': [{
                    'data': [e.nb for e in etapes_qs],
                    'backgroundColor': [e.Etape.couleur for e in etapes_qs]
                }]
            }
        )
