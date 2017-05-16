# -*- coding: utf-8 -*-

from getpass import getpass
import os
import re
import time

from flask import render_template
from flask_mail import Mail, Message
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from .importers.adresses import AdressesImporter
from .importers.etapes import EtapesImporter
from .importers.nosdeputes import NosDeputesImporter

from .irfm import app

from .models import db, Etape, Parlementaire
from .models.constants import ETAPE_NA

from .tools.files import generer_demande
from .tools.text import hash_password


manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)


@manager.command
def clear_cache():
    """Vide le cache des fichiers générés"""
    files_root = os.path.join(app.config['DATA_DIR'], 'files')
    if os.path.exists(files_root):
        for item in os.listdir(files_root):
            print('Suppression %s' % item)
            os.unlink(os.path.join(files_root, item))


@manager.command
@manager.option('--envoyer', action='store_true')
def envoyer_emails(envoyer=False):
    """Envoie des e-mails pour tous les parlementaires"""
    app.config.update(SQLALCHEMY_ECHO=False)

    files_root = os.path.join(app.config['DATA_DIR'], 'files')

    mail = Mail(app)
    parls = Parlementaire.query.join(Parlementaire.etape) \
                               .filter(Etape.ordre > ETAPE_NA) \
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

        print('[%s/%s] Envoi mail à %s (%s)' % (total, len(parls),
                                                parl.nom_complet,
                                                ', '.join(recipients)))
        mail.send(msg)

        if envoyer:
            parl.mails_envoyes = 1
            db.session.commit()

        time.sleep(1)

    print('')
    if len(missed_addr):
        print('Parlementaires sans adresse postale :\n')
        print('\n'.join(missed_addr))
    else:
        print('Aucun parlementaire sans adresse postale :)')

    print('')
    if len(missed_email):
        print('Parlementaires sans adresse mail:\n')
        print('\n'.join(missed_email))
    else:
        print('Aucun parlementaire sans adresse mail :)')


@manager.command
def generer_demandes():
    """Génère les demandes pour tous les parlementaires"""
    app.config.update(SQLALCHEMY_ECHO=False)

    files_root = os.path.join(app.config['DATA_DIR'], 'files')
    parls = Parlementaire.query.join(Parlementaire.etape) \
                               .filter(Etape.ordre > ETAPE_NA) \
                               .order_by(Parlementaire.nom) \
                               .all()

    missed = []
    for parl in parls:
        if not parl.adresse:
            missed.append(parl.nom_complet)
            continue

        print(parl.nom_complet)
        generer_demande(parl, files_root, True)

    print('')
    if len(missed):
        print('Parlementaires sans adresse:\n')
        print('\n'.join(missed))
    else:
        print('Aucun parlementaire sans adresse :)')


@manager.command
def import_etapes():
    """Crée ou met à jour la liste des étapes"""
    app.config.update(SQLALCHEMY_ECHO=False)
    EtapesImporter(app).run()


@manager.command
def import_nd():
    """Importe les députés depuis NosDéputés.fr"""
    app.config.update(SQLALCHEMY_ECHO=False)
    NosDeputesImporter(app).run()


@manager.command
def import_adresses():
    """Importe adresses postales des parlementaires"""
    app.config.update(SQLALCHEMY_ECHO=False)
    AdressesImporter(app).run()


@manager.command
def password():
    """Chiffre un mot de passe admin"""
    print(hash_password(getpass(), app.config['SECRET_KEY']))


@manager.command
def runserver():
    """Exécute le serveur web flask intégré"""
    app.run()
