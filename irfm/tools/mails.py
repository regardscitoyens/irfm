# -*- coding: utf-8 -*-

import os
import time

from flask import render_template

from flask_mail import Mail, Message

from ..models import User, Parlementaire, db
from ..models.constants import ETAPE_NA

from ..tools.files import generer_demande


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


def envoyer_alerte(app, etape, parl, commentaire):
    mail = Mail(app)

    sender = ('Regards Citoyens', app.config['ADMIN_EMAIL'])
    subject = 'Transparence IRFM - Alerte pour %s' % parl.nom_complet

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
