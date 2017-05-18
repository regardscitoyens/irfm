# -*- coding: utf-8 -*-

from flask import session, url_for

from ..models import Action, Etape
from ..models.constants import (CHAMBRES, ETAPES, ETAPES_BY_ORDRE,
                                ETAPE_AR_RECU, ETAPE_A_CONFIRMER,
                                ETAPE_A_ENVOYER, ETAPE_COM_A_MODERER,
                                ETAPE_COM_PUBLIE, ETAPE_ENVOYE, ETAPE_NA,
                                ETAPE_REPONSE_POSITIVE)


def setup(app):

    @app.context_processor
    def inject_user_info():
        return {
            'is_logged': bool(session.get('user')),
            'is_admin': session.get('user') and session['user']['admin']
        }

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
                'url': url_for('historique'),
                'label': 'Historique de l\'IRFM',
                'endpoint': 'historique',
            },
            {
                'url': url_for('faq'),
                'label': 'FAQ',
                'endpoint': 'faq',
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
                    'label': '<span class="admin">À confirmer</span>',
                    'endpoint': 'admin_en_attente"'
                }
            ]

            nb_moderer = Action.query \
                               .join(Action.etape) \
                               .filter(Etape.ordre == ETAPE_COM_A_MODERER) \
                               .count()

            if nb_moderer > 0:
                menu += [
                    {
                        'url': url_for('admin_commentaires'),
                        'label': '<span class="admin">À modérer (%s)</span>'
                                 % nb_moderer,
                        'endpoint': 'admin_commentaires'
                    }
                ]

        return {'menu': menu}

    @app.context_processor
    def inject_constante():
        return {
            'etapes_by_ordre': ETAPES_BY_ORDRE,
            'etapes': ETAPES,
            'ordres': {
                'ETAPE_NA': ETAPE_NA,
                'ETAPE_A_ENVOYER': ETAPE_A_ENVOYER,
                'ETAPE_A_CONFIRMER': ETAPE_A_CONFIRMER,
                'ETAPE_ENVOYE': ETAPE_ENVOYE,
                'ETAPE_AR_RECU': ETAPE_AR_RECU,
                'ETAPE_COM_A_MODERER': ETAPE_COM_A_MODERER,
                'ETAPE_COM_PUBLIE': ETAPE_COM_PUBLIE,
                'ETAPE_REPONSE_POSITIVE': ETAPE_REPONSE_POSITIVE
            },
            'chambres': CHAMBRES
        }
