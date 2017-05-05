# -*- coding: utf-8 -*-

#
# Lors de la modification de ces énumérations, penser à créer une migration DB
# pour mettre à jour les types ENUM correspondants en base de données.
#

CHAMBRES = {
    'AN': 'Assemblée nationale',
    'SEN': 'Sénat',
}

ETAPES = {
    'NOUVEAU': 'Nouveau'
}

SEXES = {
    'F': 'Femme',
    'H': 'Homme',
}
