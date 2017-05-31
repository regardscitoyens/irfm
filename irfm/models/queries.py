# -*- coding: utf-8 -*-

from sqlalchemy.sql.expression import case, func

from .constants import (ETAPE_A_CONFIRMER, ETAPE_A_ENVOYER, ETAPE_ENVOYE,
                        ETAPE_NA, ETAPES)
from .database import db
from .parlementaire import Parlementaire
from .procedure import Action


def etat_courriers():
    """
    Renvoie les données pour constituer un histogramme des états des courriers.
    """

    _etats = [
        'Inconnu',
        'Pris en charge',
        'En cours de traitement',
        'En attente de seconde présentation',
        'Pli présenté',
        'Attend d\'être retiré au guichet',
        'Distribué',
    ]

    # Extrait "Distribué" de "1X23456: Distribué (01/02/2017)"
    expr = func.split_part(
        func.split_part(
            Action.suivi, ':', 2),
        ' (', 1
    )

    data = {item.etat if len(item.etat) else 'Inconnu': item.nb
            for item in db.session.query(expr.label('etat'),
                                         func.count(1).label('nb'))
                                  .filter(Action.etape == ETAPE_ENVOYE)
                                  .group_by(expr)
                                  .all()}

    return [(etat, data.get(etat, 0)) for etat in _etats]


def par_departement():
    """
    Renvoie chaque département avec le nombre total de parlementaires, le
    nombre à chaque étape, le nombre >= pris en charge, le nombre >= envoyé
    """

    # Comptage des parlementaires par département...
    dept_qs = db.session \
                .query(Parlementaire.num_deptmt,
                       func.count(Parlementaire.id).label('total'))

    # ...et par étape
    dept_qs = dept_qs.add_columns(*[
        func.sum(case([(Parlementaire.etape == e['ordre'], 1)], else_=0))
        .label('nb_etape_%s' % e['ordre'])
        for e in ETAPES
    ])

    # ...et qui sont dans une étape >= pris en charge
    dept_qs = dept_qs.add_columns(
        func.sum(case([(Parlementaire.etape >= ETAPE_A_CONFIRMER, 1)],
                      else_=0)).label('nb_prisencharge'),
        func.sum(case([(Parlementaire.etape >= ETAPE_ENVOYE, 1)],
                      else_=0)).label('nb_envoyes')
    )

    return dept_qs.group_by(Parlementaire.num_deptmt) \
                  .order_by(Parlementaire.num_deptmt) \
                  .all()


def par_etape():
    """
    Renvoie les étapes avec le nombre de parlementaires par étape
    """

    count = func.count(Parlementaire.id)
    return db.session.query(Parlementaire.etape, count.label('nb')) \
                     .filter(Parlementaire.etape > ETAPE_NA) \
                     .group_by(Parlementaire.etape) \
                     .order_by(Parlementaire.etape) \
                     .having(count > 0) \
                     .all()


def random_parl():
    """
    Renvoie un parlementaire au hasard parmi ceux à l'état "À envoyer", ou si
    aucun n'est disponible parmi ceux concernés par l'opération
    """

    parl = Parlementaire.query \
                        .filter(Parlementaire.etape == ETAPE_A_ENVOYER) \
                        .order_by(func.random()) \
                        .first()

    if not parl:
        parl = Parlementaire.query \
                            .filter(Parlementaire.etape > ETAPE_NA) \
                            .order_by(func.random()) \
                            .first()

    return parl
