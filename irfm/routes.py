# -*- coding: utf-8 -*-

from flask import render_template
from sqlalchemy.orm import joinedload, contains_eager
from sqlalchemy.sql.expression import func

from .models import db, Etape, Parlementaire


def setup_routes(app):

    @app.context_processor
    def inject_piwik():
        piwik = None
        if app.config['PIWIK_HOST']:
            piwik = {
                'host': app.config['PIWIK_HOST'],
                'id': app.config['PIWIK_ID']
            }

        return {'piwik':piwik}


    @app.context_processor
    def inject_menu():
        return {
            'menu': [
                {'url': '/', 'label': 'Accueil', 'endpoint': 'home' },
                {'url': '/parlementaires', 'label': 'Liste des parlementaires',
                 'endpoint': 'parlementaires' },
            ]
        }


    @app.route('/', endpoint='home')
    def home():
        pqs = Parlementaire.query.options(joinedload(Parlementaire.etape)) \
                                 .filter(Etape.label == 'À envoyer') \
                                 .order_by(func.random())

        eqs = db.session.query(Etape) \
                        .outerjoin(Etape.parlementaires) \
                        .add_columns(func.count(Parlementaire.id)
                                         .label('nb')) \
                        .filter(Etape.ordre > 0) \
                        .group_by(Etape) \
                        .order_by(Etape.ordre) \
                        .all()

        return render_template(
            'index.html.j2',
            parlementaire=pqs.first(),
            etapes={
                'labels': [e.Etape.label for e in eqs],
                'couleurs': [e.Etape.couleur for e in eqs],
                'counts': [e.nb for e in eqs]
            }
        )


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
