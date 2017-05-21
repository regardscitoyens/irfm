# -*- coding: utf-8 -*-

from flask import render_template

from sqlalchemy.sql.expression import case, func

from ..models import Parlementaire, db
from ..models.constants import (ETAPES, ETAPES_BY_ORDRE, ETAPE_A_ENVOYER,
                                ETAPE_ENVOYE, ETAPE_NA)


def setup_routes(app):

    @app.route('/', endpoint='home')
    def home():
        # Un parlementaire à l'étape "à envoyer" au hasard
        parl = Parlementaire.query \
                            .filter(Parlementaire.etape == ETAPE_A_ENVOYER) \
                            .order_by(func.random()) \
                            .first()

        # Toutes les étapes avec le nombre de parlementaires à cette étape
        etapes_qs = db.session \
                      .query(Parlementaire.etape,
                             func.count(Parlementaire.id).label('nb')) \
                      .filter(Parlementaire.etape > ETAPE_NA) \
                      .group_by(Parlementaire.etape) \
                      .order_by(Parlementaire.etape) \
                      .all()

        # Comptage des parlementaires par département...
        dept_qs = db.session \
                    .query(Parlementaire.num_deptmt,
                           func.count(Parlementaire.id).label('total'))

        # ...et par étape
        dept_qs = dept_qs.add_columns(*[
            func.sum(case([(Parlementaire.etape == e['ordre'], 1)], else_=0))
            .label('nb_etape_%s' % e['ordre'])
            for e in ETAPES
        ])

        # ...et qui sont dans une étape >= envoyé
        dept_qs = dept_qs.add_columns(
            func.sum(case([(Parlementaire.etape >= ETAPE_ENVOYE, 1)], else_=0))
            .label('nb_envoyes')
        )

        dept_qs = dept_qs.group_by(Parlementaire.num_deptmt) \
                         .order_by(Parlementaire.num_deptmt) \
                         .all()

        def for_nz(getter):
            return [getter(e) for e in etapes_qs if e.nb > 0]

        def key_for_nz(key):
            return for_nz(lambda e: ETAPES_BY_ORDRE[e.etape][key])

        return render_template(
            'index.html.j2',
            parlementaire=parl,
            etapes_data={
                'labels': key_for_nz('label'),
                'datasets': [{
                    'data': for_nz(lambda e: e.nb),
                    'backgroundColor': key_for_nz('couleur'),
                    'hoverBackgroundColor': key_for_nz('couleur'),
                    'borderWidth': for_nz(lambda e: 0)
                }]
            },
            departements=dept_qs
        )

    @app.route('/faq', endpoint='faq')
    def faq():
        return render_template('markdown.html.j2',
                               title='Foire aux Questions',
                               file='text/FAQ.md')

    @app.route('/historique', endpoint='historique')
    def historique():
        return render_template('markdown.html.j2',
                               title='Quel est l\'historique de l\'IRFM ?',
                               file='text/historique.md')
