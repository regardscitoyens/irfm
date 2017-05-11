# -*- coding: utf-8 -*-

EXTENSIONS = {
    'pdf': 'application/pdf',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
}

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

ETAPE_NA = 0
ETAPE_A_ENVOYER = 10
ETAPE_A_CONFIRMER = 15
ETAPE_ENVOYE = 20
ETAPE_AR_RECU = 30

ETAPES = [
    {
        'ordre': ETAPE_NA,
        'label': 'N/A',
        'description': '',
        'couleur': '',
        'icone': '',
    },
    {
        'ordre': ETAPE_A_ENVOYER,
        'label': 'À envoyer',
        'description': """
            La demande d'accès aux relevés de comptes du parlementaire n'a pas
            encore été envoyée.
        """,
        'couleur': '#aaaaaa',
        'icone': 'envelope-open',
    },
    {
        'ordre': ETAPE_A_CONFIRMER,
        'label': 'À confirmer',
        'description': """
            Un utilisateur a souhaité se charger de l'envoi de la demande, mais
            nous n'avons pas encore confirmation de cet envoi.
        """,
        'couleur': '#666699',
        'icone': 'clock-o',
    },
    {
        'ordre': ETAPE_ENVOYE,
        'label': 'Envoyé',
        'description': """
            La demande d'accès aux relevés de comptes du parlementaire a été
            envoyée, mais nous n'avons pas encore d'avis de réception.
        """,
        'couleur': '#66bbbb',
        'icone': 'envelope'
    },
    {
        'ordre': ETAPE_AR_RECU,
        'label': 'AR reçu',
        'description': """
            Le parlementaire a reçu la demande d'accès à ses relevés de
            comptes.
        """,
        'couleur': '#6666bb',
        'icone': 'check'
    },
    {
        'ordre': 40,
        'label': 'Réponse positive',
        'description': """
            Le parlementaire nous a transmis les relevés de compte demandés.
        """,
        'couleur': '#66bb66',
        'icone': 'smile-o',
    },
    {
        'ordre': 45,
        'label': 'Réponse partielle',
        'description': """
            Le parlementaire accepté de nous transmettre une partie des
            documents demandés.
        """,
        'couleur': '#ddbb66',
        'icone': 'meh-o',
    },
    {
        'ordre': 50,
        'label': 'Réponse négative',
        'description': """
            Le parlementaire a refusé de nous transmettre ses relevés de
            compte, soit explicitement, soit par voie de presse, soit à
            l'expiration d'un délai de 2 mois après réception de la demande.
        """,
        'couleur': '#bb6666',
        'icone': 'frown-o',
    },
]

ETAPES_BY_ORDRE = {e['ordre']: e for e in ETAPES}
