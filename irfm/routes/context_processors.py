# -*- coding: utf-8 -*-

from datetime import datetime

from flask import session, url_for

from ..models import Action, Parlementaire, User
from ..models.constants import (CHAMBRES, ETAPES, ETAPES_BY_ORDRE,
                                ETAPE_AR_RECU, ETAPE_A_CONFIRMER,
                                ETAPE_A_ENVOYER, ETAPE_COM_A_MODERER,
                                ETAPE_COM_PUBLIE, ETAPE_COURRIEL,
                                ETAPE_DOC_MASQUE, ETAPE_DOC_PUBLIE,
                                ETAPE_ENVOYE, ETAPE_NA, ETAPE_REPONSE_NEGATIVE,
                                ETAPE_REPONSE_POSITIVE, ETAPE_DEMANDE_CADA)


def setup(app):

    @app.context_processor
    def inject_timestamp():
        return {
            'manet_timestamp': int(datetime.now().timestamp() / 3600)
        }

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
                'label': 'Qu\'est-ce que l\'IRFM ?',
                'endpoint': 'historique',
            },
            {
                'url': url_for('derives'),
                'label': 'Les dérives de l\'IRFM',
                'endpoint': 'derives',
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

        if session.get('user'):
            acts = Action.query \
                         .filter(Parlementaire.id == Action.parlementaire_id) \
                         .filter(Action.etape == ETAPE_A_CONFIRMER) \
                         .filter(Action.user_id == session['user']['id']) \
                         .exists()

            nb = Parlementaire.query.filter(acts) \
                                    .filter(Parlementaire.etape ==
                                            ETAPE_A_CONFIRMER) \
                                    .count()

            label = 'Mes actions'
            if nb > 0:
                title = '%s envoi%s à confirmer' % (nb, 's' if nb > 1 else '')
                label += ' <span class="badge" data-toggle="tooltip" ' \
                         'title="%s">%s</span>' % (title, nb)

            menu += [
                {
                    'url': url_for('mes_actions'),
                    'label': '%s' % label,
                    'endpoint': 'mes_actions'
                }
            ]

        if session.get('user') and session.get('user')['admin']:
            menu += [
                {
                    'url': url_for('admin_recent'),
                    'label': '<span class="admin">Actions récentes</span>',
                    'endpoint': 'admin_recent'
                }
            ]

            nb_aconfirmer = Parlementaire.query \
                .filter(Parlementaire.etape == ETAPE_A_CONFIRMER).count()

            if nb_aconfirmer > 0:
                badge = ' <span class="badge">%s</span>' % nb_aconfirmer
                menu += [
                    {
                        'url': url_for('admin_en_attente'),
                        'label': '<span class="admin">À confirmer</span> %s'
                                 % badge,
                        'endpoint': 'admin_en_attente'
                    }
                ]

            nb_moderer = Action.query \
                               .join(Action.user) \
                               .filter(Action.etape == ETAPE_COM_A_MODERER) \
                               .filter(User.nick != '!rc') \
                               .count()

            if nb_moderer > 0:
                badge = ' <span class="badge">%s</span>' % nb_moderer
                menu += [
                    {
                        'url': url_for('admin_commentaires'),
                        'label': '<span class="admin">À modérer</span> %s'
                                 % badge,
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
                'ETAPE_COM_PUBLIE': ETAPE_COM_PUBLIE,
                'ETAPE_COM_A_MODERER': ETAPE_COM_A_MODERER,
                'ETAPE_DOC_MASQUE': ETAPE_DOC_MASQUE,
                'ETAPE_DOC_PUBLIE': ETAPE_DOC_PUBLIE,
                'ETAPE_COURRIEL': ETAPE_COURRIEL,
                'ETAPE_NA': ETAPE_NA,
                'ETAPE_A_ENVOYER': ETAPE_A_ENVOYER,
                'ETAPE_A_CONFIRMER': ETAPE_A_CONFIRMER,
                'ETAPE_ENVOYE': ETAPE_ENVOYE,
                'ETAPE_AR_RECU': ETAPE_AR_RECU,
                'ETAPE_REPONSE_POSITIVE': ETAPE_REPONSE_POSITIVE,
                'ETAPE_REPONSE_NEGATIVE': ETAPE_REPONSE_NEGATIVE,
                'ETAPE_DEMANDE_CADA': ETAPE_DEMANDE_CADA
            },
            'chambres': CHAMBRES
        }
