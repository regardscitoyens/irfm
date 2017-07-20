# -*- coding: utf-8 -*-

from datetime import datetime, time

from ..models import Action, Parlementaire, User, db
from ..models.constants import (DEBUT_ACTION, ETAPE_COURRIEL, ETAPES_BY_ORDRE,
                                ETAPE_DEMANDE_CADA, ETAPE_REPONSE_POSITIVE,
                                ETAPE_NA)

from .mails import envoyer_alerte


def fix_procedure(app):

    # Ajout étape "email" aux parlementaires qui ne l'ont pas
    acts = Action.query.filter(Parlementaire.id == Action.parlementaire_id) \
                       .filter(Action.etape == ETAPE_COURRIEL) \
                       .exists()

    parls = Parlementaire.query.filter(Parlementaire.mails_envoyes == 1) \
                               .filter(~acts) \
                               .order_by(Parlementaire.nom) \
                               .all()

    admin = User.query.filter(User.nick == '!rc').one()

    for parl in parls:
        print('%s: etape courriel' % parl.nom_complet)

        act = Action(
            parlementaire=parl,
            etape=ETAPE_COURRIEL,
            date=datetime.combine(DEBUT_ACTION, time(23, 30)),
            user=admin
        )
        db.session.add(act)

    db.session.commit()


def avance_procedure(app, ordre_etape):
    etape = ETAPES_BY_ORDRE.get(ordre_etape, None)
    admin = User.query.filter(User.nick == '!rc').one()

    if ordre_etape == ETAPE_DEMANDE_CADA:
        # Recherche des parlementaire n'ayant pas de réponse positive
        # et avant l'étape CADA
        query = Parlementaire.query \
            .filter(Parlementaire.etape != ETAPE_REPONSE_POSITIVE) \
            .filter(Parlementaire.etape < ETAPE_DEMANDE_CADA)
    elif etape:
        print('Etape non supportée : %s' % etape['label'])
        return
    else:
        print('Etape inconnue : %s' % ordre_etape)
        return

    # Filtrage (générique) des parlementaires concernés par l'opération et qui
    # ne sont pas déjà à cette étape
    parls = query.filter(Parlementaire.etape != ordre_etape) \
        .filter(Parlementaire.etape > ETAPE_NA) \
        .all()

    for parl in parls:
        print(parl.nom_complet)

        # Création de l'action
        act = Action(
            parlementaire=parl,
            etape=ordre_etape,
            date=datetime.now(),
            user=admin,
        )
        db.session.add(act)
        parl.etape = ordre_etape

        # Commit immédiat pour pouvoir arrêter en plein milieu et reprendre
        db.session.commit()

        if etape['alerte']:
            cnt = envoyer_alerte(app, etape, parl, '')
            if cnt:
                print('%s e-mails d\'alerte envoyés' % cnt)

        # Throttling mails
        time.sleep(1)
