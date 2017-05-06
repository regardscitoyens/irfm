# -*- coding: utf-8 -*-

from flask import url_for


def setup(app):

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
                {
                    'url': url_for('home'),
                    'label': 'Accueil',
                    'endpoint': 'home',
                },
                {
                    'url': url_for('parlementaires'),
                    'label': 'Liste des parlementaires',
                    'endpoint': 'parlementaires',
                },
            ]
        }
