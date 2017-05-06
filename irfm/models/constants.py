# -*- coding: utf-8 -*-

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

ETAPES = [
    {
        'ordre': 0,
        'label': 'N/A',
        'description': '',
        'couleur': '',
    },
    {
        'ordre': 10,
        'label': 'À envoyer',
        'description': '',
        'couleur': '#cccccc',
    },
    {
        'ordre': 20,
        'label': 'Envoyé',
        'description': '',
        'couleur': '#88dddd',
    },
    {
        'ordre': 30,
        'label': 'AR reçu',
        'description': '',
        'couleur': '#8888dd',
    },
    {
        'ordre': 40,
        'label': 'Réponse positive',
        'description': '',
        'couleur': '#88dd88',
    },
    {
        'ordre': 50,
        'label': 'Réponse négative',
        'description': '',
        'couleur': '#dd8888',
    },
    {
        'ordre': 60,
        'label': 'Demande CADA',
        'description': '',
        'couleur': '#ddaa88',
    },
    {
        'ordre': 70,
        'label': 'Accord CADA',
        'description': '',
        'couleur': '#44aa44',
    },
    {
        'ordre': 90,
        'label': 'Refus CADA',
        'description': '',
        'couleur': '#aa4444',
    },
]
