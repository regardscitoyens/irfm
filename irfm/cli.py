# -*- coding: utf-8 -*-

import os
from getpass import getpass

from flask_migrate import Migrate, MigrateCommand

from flask_script import Manager

from .importers.adresses import AdressesImporter
from .importers.etapes import EtapesImporter
from .importers.nosdeputes import NosDeputesImporter

from .irfm import app

from .models import db

from .tools.files import generer_demandes as generer_demandes_
from .tools.mails import envoyer_emails as envoyer_emails_
from .tools.procedure import fix_procedure as fix_procedure_
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
    missed_addr, missed_email = envoyer_emails_(app, envoyer)

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
def fix_procedure():
    """Génère les étapes manquantes pour tous les parlementaires"""
    app.config.update(SQLALCHEMY_ECHO=False)
    fix_procedure_(app)


@manager.command
def generer_demandes():
    """Génère les demandes pour tous les parlementaires"""
    app.config.update(SQLALCHEMY_ECHO=False)
    missed = generer_demandes_(app)

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
