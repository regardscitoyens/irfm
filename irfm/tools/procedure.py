# -*- coding: utf-8 -*-

from datetime import datetime, time

from ..models import Action, Parlementaire, db
from ..models.constants import DEBUT_ACTION, ETAPE_COURRIEL


def fix_procedure(app):

    # Ajout étape "email" aux parlementaires qui ne l'ont pas
    acts = Action.query.filter(Parlementaire.id == Action.parlementaire_id) \
                       .filter(Action.etape == ETAPE_COURRIEL) \
                       .exists()

    parls = Parlementaire.query.filter(Parlementaire.mails_envoyes == 1) \
                               .filter(~acts) \
                               .order_by(Parlementaire.nom) \
                               .all()

    for parl in parls:
        print('%s: etape courriel' % parl.nom_complet)

        act = Action(
            parlementaire=parl,
            etape=ETAPE_COURRIEL,
            date=datetime.combine(DEBUT_ACTION, time(23, 30)),
            nick='!rc',
            email=app.config['ADMIN_EMAIL'],
        )
        db.session.add(act)

    db.session.commit()
