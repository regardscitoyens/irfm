# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import email
import os
import re
import subprocess
import time

from flask import render_template

from flask_mail import Mail, Message

from sqlalchemy.orm import contains_eager, joinedload
from sqlalchemy.orm.exc import NoResultFound

from ..models import Action, User, Parlementaire, db
from ..models.constants import (DELAI_RELANCE, DELAI_REPONSE, ETAPE_NA,
                                ETAPE_A_CONFIRMER, ETAPE_DEMANDE_CADA,
                                ETAPE_DOC_MASQUE)
from ..models.functions import normalize_name

from ..tools.files import generer_demande
from ..tools.text import create_usertoken as token


def mailing_lists():
    filters = {
        'Liste Membres': User.abo_membres == True,  # noqa
        'Liste IRFM': User.abo_irfm == True,  # noqa
        'Newsletter': User.abo_rc == True,  # noqa
    }

    return {
        k: [u.email for u in User.query.filter(f).all()]
        for k, f in filters.items()
    }


def envoyer_alerte(app, etape, parl, commentaire=None):
    mail = Mail(app)

    sender = ('Regards Citoyens', app.config['ADMIN_EMAIL'])
    subject = 'Transparence IRFM - Alerte pour %s' % parl.nom_complet

    if not commentaire:
        commentaire = etape['description']

    messages = []
    for user in parl.abonnes:
        anon_id = user.nick[8:] if user.nick.startswith('anonyme!') else None
        body = render_template('courriers/mail_alerte.txt.j2',
                               user=user,
                               anon_id=anon_id,
                               etape=etape,
                               parl=parl,
                               commentaire=commentaire)

        messages.append(Message(subject=subject, body=body, sender=sender,
                                recipients=[user.email]))

    with mail.connect() as conn:
        for msg in messages:
            conn.send(msg)

    return len(messages)


def envoyer_emails(app, envoyer):
    files_root = os.path.join(app.config['DATA_DIR'], 'files')

    mail = Mail(app)
    parls = Parlementaire.query.filter(Parlementaire.etape > ETAPE_NA) \
                               .filter(Parlementaire.mails_envoyes == 0) \
                               .order_by(Parlementaire.nom) \
                               .all()

    missed_addr = []
    missed_email = []

    total = 0

    if envoyer:
        print('')
        print('ENVOI POUR DE VRAI dans 5s')
        print('')

        time.sleep(5)
    else:
        print('Envoi test, ajouter --envoyer pour le bouton rouge')

    for parl in parls:
        total += 1

        if not parl.adresse:
            missed_addr.append(parl.nom_complet)
            continue

        if not parl.emails:
            missed_email.append(parl.nom_complet)
            continue

        filename = generer_demande(parl, files_root)

        sender = ('Regards Citoyens', app.config['ADMIN_EMAIL'])
        subject = 'Demande d\'accès aux dépenses de vos frais de mandat'
        body = render_template('courriers/mail_parlementaire.txt.j2',
                               parlementaire=parl)

        if envoyer:
            recipients = parl.emails.split(',')
            bcc = [app.config['ADMIN_EMAIL']]
        else:
            subject = '[TEST] %s' % subject
            emails = ', '.join(parl.emails.split(','))
            body = '[TEST] Destinataires: %s\n\n%s' % (emails, body)

            recipients = [app.config['ADMIN_EMAIL']]
            bcc = []

        msg = Message(subject=subject, body=body, sender=sender,
                      recipients=recipients, bcc=bcc)

        with open(os.path.join(files_root, filename), 'rb') as f:
            msg.attach(filename, 'application/pdf', f.read())

        print('[%s/%s] Envoi mail à %s (%s)' %
              (total, len(parls), parl.nom_complet, ', '.join(recipients)))
        mail.send(msg)

        if envoyer:
            parl.mails_envoyes = 1
            db.session.commit()

        time.sleep(1)

    return missed_addr, missed_email


def envoyer_relances(app, envoyer):
    mail = Mail(app)

    date_min = datetime.now() - timedelta(days=DELAI_RELANCE)
    acts = Action.query.join(Action.parlementaire) \
                       .filter(Action.etape == ETAPE_A_CONFIRMER) \
                       .filter(Parlementaire.etape == ETAPE_A_CONFIRMER) \
                       .filter(Action.suivi == None) \
                       .filter(Action.date < date_min) \
                       .options(contains_eager(Action.parlementaire)) \
                       .options(joinedload(Action.user)) \
                       .order_by(Parlementaire.nom) \
                       .all()  # noqa

    data = {}

    for act in acts:
        if act.user not in data:
            data[act.user] = []
        data[act.user].append(act)

    for user, acts in data.items():
        sender = ('Regards Citoyens', app.config['ADMIN_EMAIL'])
        subject = 'Transparence IRFM - Relance'
        body = render_template('courriers/mail_relance.txt.j2',
                               user=user,
                               token=token(user.id, app.config['SECRET_KEY']),
                               parls=[a.parlementaire for a in acts],
                               delai_relance=DELAI_RELANCE,
                               delai_reponse=DELAI_REPONSE)

        msg = Message(subject=subject, body=body, sender=sender,
                      recipients=[user.email])

        if envoyer:
            mail.send(msg)
            for a in acts:
                a.suivi = 'Relancé le %s' % datetime.now().strftime('%x')
            time.sleep(1)
        else:
            print(msg)

    if envoyer:
        db.session.commit()


def erratum_cada(app):
    parls = Parlementaire.query \
        .filter(Parlementaire.etape == ETAPE_DEMANDE_CADA) \
        .all()

    mail = Mail(app)

    for parl in parls:
        print(parl.nom_complet)

        sender = ('Regards Citoyens', app.config['ADMIN_EMAIL'])
        subject = 'Transparence IRFM - Erratum - Alerte pour %s' % \
            parl.nom_complet

        messages = []
        for user in parl.abonnes:
            anon_id = user.nick[8:] if user.nick.startswith('anonyme!') \
                else None
            body = render_template('courriers/mail_erratum.txt.j2',
                                   user=user,
                                   anon_id=anon_id,
                                   parl=parl)

            messages.append(Message(subject=subject, body=body, sender=sender,
                                    recipients=[user.email]))

        if len(messages):
            with mail.connect() as conn:
                for msg in messages:
                    conn.send(msg)

            print('%s e-mails d\'erratum envoyés' % len(messages))
            time.sleep(1)


AVIS_INCOMPETENCE = 'La commission ne peut donc que se déclarer ' + \
                    'incompétente pour se prononcer sur la demande.'
AVIS_RE_DEPUTE = re.compile('par( Monsieur| Madame)+ ([^,]*),? députée?')
AVIS_EXCEPTIONS = {
    'Pierre LELLOUCH': 'Pierre LELLOUCHE'
}


def extraire_mails_cada(app):
    emails_root = os.path.join(app.config['DATA_DIR'], 'emails')
    files_root = os.path.join(app.config['DATA_DIR'], 'files')

    admin = User.query.filter(User.nick == '!rc').one()

    for eml in [f for f in os.listdir(emails_root)
                if os.path.isfile(os.path.join(emails_root, f))
                and f.endswith('.eml')]:
        remove = False
        with open(os.path.join(emails_root, eml)) as f:
            message = email.message_from_file(f)
            cada_id = message['subject']

            # Extraction pièce jointe 'Avis.pdf'
            pdf = None
            for pl in message.get_payload():
                if pl.get_filename() == 'Avis.pdf':
                    pdf = pl.get_payload(decode=True)
                    break

            if not pdf:
                print('CADA %s: (!) avis introuvable' % cada_id)
                continue

            # Enregistrement du PDF
            pdfbase = 'avis-cada-%s.pdf' % cada_id
            pdfname = os.path.join(files_root, pdfbase)
            with open(pdfname, 'wb') as outf:
                outf.write(pdf)

            # Extraction du texte
            pro = subprocess.run(['pdftotext', pdfname, '-'],
                                 stdout=subprocess.PIPE,
                                 encoding='utf-8')

            # Vérification de la décision
            if AVIS_INCOMPETENCE not in pro.stdout:
                print('CADA %s: (!) décision inattendue' % cada_id)

            # Extraction du député concerné
            match = AVIS_RE_DEPUTE.search(pro.stdout)
            if not match:
                print('CADA %s: (!) nom député introuvable' % cada_id)
                continue

            nom = match.group(2)
            nom = AVIS_EXCEPTIONS.get(nom, nom)
            condition = normalize_name(Parlementaire.nom_complet) \
                .ilike(normalize_name(nom))

            try:
                parl = Parlementaire.query.filter(condition).one()
            except NoResultFound:
                print('CADA %s: (!) parlementaire inconnu %s'
                      % (cada_id, nom))
                continue

            # Recherche d'un avis existant
            try:
                act = Action.query \
                    .filter(Action.parlementaire == parl) \
                    .filter(Action.attachment.like('avis-cada-%')) \
                    .one()
            except NoResultFound:
                act = None

            if act:
                if act.attachment != pdfbase:
                    print('CADA %s; (!) 2ème avis CADA (existant: %s)'
                          % (cada_id, pdfbase))
                continue

            print('CADA %s; Ajout avis CADA pour %s'
                  % (cada_id, parl.nom_complet))

            act = Action(
                parlementaire=parl,
                etape=ETAPE_DOC_MASQUE,
                date=datetime.now(),
                suivi='La CADA s\'est déclarée incompétente pour '
                      + 'répondre à notre demande.',
                attachment=pdfbase,
                user=admin
            )

            db.session.add(act)
            db.session.commit()

        if remove:
            os.unlink(os.path.join(emails_root, eml))

    db.session.commit()
