# -*- coding: utf-8 -*-

from flask import url_for

from ..models.constants import (ETAPE_NA, ETAPE_A_ENVOYER, ETAPE_A_CONFIRMER,
                                ETAPE_ENVOYE)


def setup(app):

    @app.context_processor
    def inject_piwik():
        piwik = None
        if app.config['PIWIK_HOST']:
            piwik = {
                'host': app.config['PIWIK_HOST'],
                'id': app.config['PIWIK_ID']
            }

        return {'piwik': piwik}

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

    @app.context_processor
    def inject_etapes():
        return {
            'ordres': {
                'ETAPE_NA': ETAPE_NA,
                'ETAPE_A_ENVOYER': ETAPE_A_ENVOYER,
                'ETAPE_A_CONFIRMER': ETAPE_A_CONFIRMER,
                'ETAPE_ENVOYE': ETAPE_ENVOYE,
            }
        }
