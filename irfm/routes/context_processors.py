# -*- coding: utf-8 -*-

from flask import session, url_for

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
        menu = [
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

        if session.get('user') and session.get('user')['admin']:
            menu += [
                {
                    'url': url_for('admin_recent'),
                    'label': '<span class="admin">Actions récentes</span>',
                    'endpoint': 'admin_recent"'
                },
                {
                    'url': url_for('admin_en_attente'),
                    'label': '<span class="admin">Actions en attente</span>',
                    'endpoint': 'admin_en_attente"'
                },
            ]

        return {'menu': menu}

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
