# -*- coding: utf-8 -*-

from flask import render_template
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import case, func

from ..models import db, Etape, Parlementaire
from ..models.constants import ETAPES, ETAPE_NA, ETAPE_A_ENVOYER, ETAPE_ENVOYE


def setup_routes(app):

    @app.route('/', endpoint='home')
    def home():
        # Un parlementaire à l'étape "à envoyer" au hasard
        parl = Parlementaire.query.join(Parlementaire.etape) \
                                  .filter(Etape.ordre == ETAPE_A_ENVOYER) \
                                  .order_by(func.random()) \
                                  .first()

        # Toutes les étapes avec le nombre de parlementaires à cette étape
        etapes_qs = db.session.query(Etape) \
                              .outerjoin(Etape.parlementaires) \
                              .add_columns(func.count(Parlementaire.id)
                                               .label('nb')) \
                              .filter(Etape.ordre > ETAPE_NA) \
                              .group_by(Etape) \
                              .order_by(Etape.ordre) \
                              .all()

        # Comptage des parlementaires par département
        dept_qs = db.session \
                    .query(Parlementaire.num_deptmt,
                           func.count(Parlementaire.id).label('total')) \
                    .join(Etape, Parlementaire.etape_id==Etape.id)


        # ...et par étape
        dept_qs = dept_qs.add_columns(*[
            func.sum(case([(Etape.ordre == e['ordre'], 1)], else_=0))
                .label('nb_etape_%s' % e['ordre'])
            for e in ETAPES
        ])

        # ...et qui sont dans une étape >= envoyé
        dept_qs = dept_qs.add_columns(
            func.sum(case([(Etape.ordre >= ETAPE_ENVOYE, 1)], else_=0))
                .label('nb_envoyes')
        )

        dept_qs = dept_qs.group_by(Parlementaire.num_deptmt) \
                         .order_by(Parlementaire.num_deptmt) \
                         .all()

        return render_template(
            'index.html.j2',
            parlementaire=parl,
            etapes_data={
                'labels': [e.Etape.label for e in etapes_qs if e.nb > 0],
                'datasets': [{
                    'data': [e.nb for e in etapes_qs if e.nb > 0],
                    'backgroundColor': [e.Etape.couleur for e in etapes_qs
                                         if e.nb > 0]
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

