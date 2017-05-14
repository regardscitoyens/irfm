# -*- coding: utf-8 -*-

from getpass import getpass
import os

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
def generer_demandes():
    """Génère les demandes pour tous les parlementaires"""
    app.config.update(SQLALCHEMY_ECHO=False)
    files_root = os.path.join(app.config['DATA_DIR'], 'files')

    parls = Parlementaire.query.join(Parlementaire.etape) \
                               .filter(Etape.ordre > ETAPE_NA) \
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
