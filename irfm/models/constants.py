# -*- coding: utf-8 -*-


import datetime


MOIS_RELEVES = 6
DEBUT_ACTION = datetime.date(2017, 5, 16)

_m = DEBUT_ACTION.month - MOIS_RELEVES
_y = DEBUT_ACTION.year
while _m < 1:
    _m = _m + 12
    _y = _y - 1

DEBUT_RELEVES = datetime.date(_y, _m, DEBUT_ACTION.day)


#
# Lors de la modification de ces énumérations, penser à créer une migration DB
# pour mettre à jour les types ENUM correspondants en base de données.
#

CHAMBRES = {
    'AN': 'Assemblée nationale',
    'SEN': 'Sénat',
}

SEXES = {
    'F': 'Femme',
    'H': 'Homme',
}

#
# Lors de la modification de cette énumération, relancer l'import des étapes.
# L'ordre est utilisé comme clé primaire lors de cet import.
#

ETAPE_COM_PUBLIE = -21
ETAPE_COM_A_MODERER = -20
ETAPE_COURRIEL = -10
ETAPE_NA = 0
ETAPE_A_ENVOYER = 10
ETAPE_A_CONFIRMER = 15
ETAPE_ENVOYE = 20
ETAPE_AR_RECU = 30
ETAPE_REPONSE_POSITIVE = 40
ETAPE_REPONSE_NEGATIVE = 50

ETAPES = [
    {
        'ordre': ETAPE_COM_PUBLIE,
        'label': 'Commentaire',
        'description': """
            Un citoyen a interpelé le parlementaire sur la transparence
            de son indemnité.
        """,
        'couleur': '#bbbbbb',
        'icone': 'commenting',
        'alerte': False,
    },
    {
        'ordre': ETAPE_COM_A_MODERER,
        'label': 'Commentaire (non publié)',
        'description': """
            Un citoyen a interpelé le parlementaire sur la transparence
            de son indemnité. Le commentaire doit être modéré avant
            publication.
        """,
        'couleur': '#bb6666',
        'icone': 'commenting',
        'alerte': False,
    },
    {
        'ordre': ETAPE_COURRIEL,
        'label': 'Courriel envoyé',
        'description': """
            La demande a été envoyée par Regards Citoyens au parlementaire
            par courriel.
        """,
        'couleur': '#66aadd',
        'icone': 'at',
        'alerte': False,
    },
    {
        'ordre': ETAPE_NA,
        'label': 'N/A',
        'description': '',
        'couleur': '',
        'icone': '',
        'alerte': False,
    },
    {
        'ordre': ETAPE_A_ENVOYER,
        'label': 'À envoyer',
        'description': """
            Aucun citoyen n'a encore pris en charge l'envoi d'une demande
            d'accès aux relevés de comptes du parlementaire.
        """,
        'couleur': '#bbbbbb',
        'icone': 'envelope-open',
        'alerte': False,
    },
    {
        'ordre': ETAPE_A_CONFIRMER,
        'label': 'Pris en charge',
        'description': """
            Un citoyen a souhaité se charger de l'envoi de la demande, mais
            nous n'avons pas encore confirmation de cet envoi.
        """,
        'couleur': '#aaaaff',
        'icone': 'clock-o',
        'alerte': False,
    },
    {
        'ordre': ETAPE_ENVOYE,
        'label': 'Envoyé',
        'description': """
            La demande d'accès aux relevés de comptes du parlementaire a été
            envoyée, mais nous n'avons pas encore d'avis de réception.
        """,
        'couleur': '#8888dd',
        'icone': 'envelope',
        'alerte': False,
    },
    {
        'ordre': ETAPE_AR_RECU,
        'label': 'AR reçu',
        'description': """
            Le parlementaire a bien reçu la demande d'accès à ses relevés de
            comptes, nous avons reçu son accusé de réception.
        """,
        'couleur': '#4444bb',
        'icone': 'check',
        'alerte': False,
    },
    {
        'ordre': ETAPE_REPONSE_POSITIVE,
        'label': 'Réponse positive',
        'description': """
            Le parlementaire nous a transmis les relevés de compte demandés
            nous a annoncé son intention de le faire.
        """,
        'couleur': '#66bb66',
        'icone': 'heart',
        'alerte': True,
    },
    {
        'ordre': ETAPE_REPONSE_NEGATIVE,
        'label': 'Réponse négative',
        'description': """
            Le parlementaire a refusé de nous transmettre ses relevés de
            compte, soit explicitement, soit par voie de presse, soit à
            l'expiration d'un délai d'un mois après réception de la demande.
        """,
        'couleur': '#bb6666',
        'icone': 'thumbs-down',
        'alerte': True,
    },
]

ETAPES_BY_ORDRE = {e['ordre']: e for e in ETAPES}
