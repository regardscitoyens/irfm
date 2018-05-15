# -*- coding: utf-8 -*-

from datetime import datetime, time
from time import sleep

from sqlalchemy.orm import joinedload

from ..models import Action, Parlementaire, User, db
from ..models.constants import (DEBUT_ACTION, ETAPE_A_CONFIRMER,
                                ETAPE_COURRIEL, ETAPES_BY_ORDRE,
                                ETAPE_DEMANDE_CADA, ETAPE_DOC_PUBLIE,
                                ETAPE_REPONSE_NEGATIVE, ETAPE_REQUETE_TA,
                                ETAPE_DOC_MASQUE, ETAPE_ENVOYE, ETAPE_AR_RECU,
                                ETAPE_REPONSE_POSITIVE, ETAPE_NA,
                                ETAPE_INCOMPETENCE_CADA)

from .mails import envoyer_alerte
from .text import slugify


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

    if ordre_etape in (ETAPE_DEMANDE_CADA, ETAPE_INCOMPETENCE_CADA,
                       ETAPE_REQUETE_TA):
        # Recherche des parlementaire n'ayant pas de réponse positive
        # et avant l'étape demandée
        query = Parlementaire.query \
            .filter(Parlementaire.etape != ETAPE_REPONSE_POSITIVE) \
            .filter(Parlementaire.etape < ordre_etape)
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
        .order_by(Parlementaire.nom) \
        .all()

    for parl in parls:
        print(parl.nom_complet)
        act = None

        # Cas particulier demande CADA
        if ordre_etape == ETAPE_DEMANDE_CADA:
            if parl.etape == ETAPE_A_CONFIRMER:
                # Suppression de l'étape prise en charge si c'est l'étape
                # actuelle du député
                pec = Action.query \
                            .filter(Action.parlementaire == parl) \
                            .filter(Action.etape == ETAPE_A_CONFIRMER) \
                            .first()
                if pec:
                    db.session.delete(pec)

            # Transformation de l'action 'Document' en action "Demande CADA"
            act = Action.query \
                        .filter(Action.parlementaire == parl) \
                        .filter(Action.etape == ETAPE_DOC_PUBLIE) \
                        .filter(Action.attachment.like('document-cada-%')) \
                        .first()
            if act:
                act.etape = ETAPE_DEMANDE_CADA

        # Cas particulier incompétence CADA
        if ordre_etape == ETAPE_INCOMPETENCE_CADA:
            # Transformation de l'action 'Document' avec l'avis CADA en action
            # "incompétence cada"
            act = Action.query \
                        .filter(Action.parlementaire == parl) \
                        .filter(Action.etape == ETAPE_DOC_MASQUE) \
                        .filter(Action.attachment.like('avis-cada-%')) \
                        .first()
            if act:
                act.etape = ETAPE_INCOMPETENCE_CADA

        # Création de l'action si inexistante
        if not act:
            act = Action(
                parlementaire=parl,
                etape=ordre_etape,
                date=datetime.now(),
                user=admin
            )

            if ordre_etape == ETAPE_REQUETE_TA:
                act.suivi = etape['description'].strip()
                act.attachment = 'requete-ta-%s.pdf' % \
                    slugify(parl.nom_complet)

            db.session.add(act)

        parl.etape = ordre_etape

        # Commit immédiat pour pouvoir arrêter en plein milieu et reprendre
        db.session.commit()

        if etape['alerte'] and not app.config['MAIL_SUPPRESS_SEND']:
            cnt = envoyer_alerte(app, etape, parl)
            if cnt:
                print('%s e-mails d\'alerte envoyés' % cnt)
                sleep(1)


def export_pour_ta(app):
    parls = Parlementaire.query.filter(Parlementaire.etape >=
                                       ETAPE_DEMANDE_CADA) \
                               .options(joinedload(Parlementaire.actions)) \
                               .order_by(Parlementaire.nom) \
                               .all()

    output_order = ['num', 'nom', 'slug', 'sexe', 'adresse', 'refus',
                    'demande', 'bordereau', 'cada_no', 'avis_cada',
                    'date_cada', 'lar_envoi', 'lar_reception']

    print(';'.join(output_order))

    parl_num = 0
    for parl in parls:
        parl_num = parl_num + 1

        data = {
            'num': '%03d' % parl_num,
            'nom': parl.nom_complet,
            'slug': slugify(parl.nom_complet),
            'sexe': parl.sexe,
            'refus': ' ',
            'demande': 'demande-irfm-%s.pdf' % slugify(parl.nom_complet),
            'adresse': parl.adresse.replace('\n', ', ').replace(',,', ',')
                                                       .replace("\xa0", " ")
        }

        for act in parl.actions:
            if act.etape == ETAPE_ENVOYE:
                data['bordereau'] = act.attachment or 'NONE'
                data['lar_envoi'] = act.date.strftime('%d %B %Y')

            if act.etape == ETAPE_AR_RECU:
                data['lar_reception'] = act.date.strftime('%d %B %Y')

            if act.etape == ETAPE_REPONSE_NEGATIVE:
                data['refus'] = 'REFUS'

            if act.etape == ETAPE_DOC_MASQUE and \
                    act.attachment.startswith('avis-cada'):
                data['avis_cada'] = act.attachment or 'NONE'
                data['date_cada'] = act.date.strftime('%d %B %Y')
                data['cada_no'] = data['avis_cada'].replace('avis-cada-', '') \
                                                   .replace('.pdf', '')

        print(';'.join([data.get(k, '') for k in output_order]))
