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

ETAPES = [
    {
        'ordre': ETAPE_NA,
        'label': 'N/A',
        'description': '',
        'couleur': '',
    },
    {
        'ordre': ETAPE_A_ENVOYER,
        'label': 'À envoyer',
        'description': """
            La demande d'accès aux relevés de comptes du parlementaire n'a pas
            encore été envoyée.
        """,
        'couleur': '#cccccc',
    },
    {
        'ordre': ETAPE_A_CONFIRMER,
        'label': 'À confirmer',
        'description': """
            Un utilisateur a souhaité se charger de l'envoi de la demande, mais
            nous n'avons pas encore confirmation de cet envoi.
        """,
        'couleur': '#8888aa',
    },
    {
        'ordre': ETAPE_ENVOYE,
        'label': 'Envoyé',
        'description': """
            La demande d'accès aux relevés de comptes du parlementaire a été
            envoyée, mais nous n'avons pas encore d'avis de réception.
        """,
        'couleur': '#88dddd',
    },
    {
        'ordre': 30,
        'label': 'AR reçu',
        'description': """
            Le parlementaire a reçu la demande d'accès à ses relevés de
            comptes.
        """,
        'couleur': '#8888dd',
    },
    {
        'ordre': 40,
        'label': 'Réponse positive',
        'description': """
            Le parlementaire nous a transmis les relevés de compte demandés.
        """,
        'couleur': '#88dd88',
    },
    {
        'ordre': 45,
        'label': 'Réponse partielle',
        'description': """
            Le parlementaire accepté de nous transmettre une partie des
            documents demandés.
        """,
        'couleur': '#ddaa88',
    },
    {
        'ordre': 50,
        'label': 'Réponse négative',
        'description': """
            Le parlementaire a refusé de nous transmettre ses relevés de
            compte, soit explicitement, soit par voie de presse, soit à
            l'expiration d'un délai de 2 mois après réception de la demande.
        """,
        'couleur': '#dd8888',
    },
]
