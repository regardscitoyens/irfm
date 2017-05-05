# -*- coding: utf-8 -*-

from flask import render_template
from sqlalchemy.orm import joinedload

from .models import Parlementaire


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
        return render_template('index.html.j2')


    @app.route('/parlementaires', endpoint='parlementaires')
    def parlementaires():
        qs = Parlementaire.query.options(joinedload('groupe')).all()
        return render_template(
            'list.html.j2',
            parlementaires=qs
        )
