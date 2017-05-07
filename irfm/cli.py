# -*- coding: utf-8 -*-

from getpass import getpass
import hmac

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from .importers.adresses import AdressesImporter
from .importers.etapes import EtapesImporter
from .importers.nosdeputes import NosDeputesImporter

from .irfm import app
from .models import db


manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)


@manager.command
def runserver():
    """Exécute le serveur web flask intégré"""
    app.run()


@manager.command
def password():
    """Chiffre un mot de passe admin"""

    h = hmac.new(bytes(app.config['SECRET_KEY'], encoding='ascii'))
    h.update(bytes(getpass(), encoding='utf-8'))
    print(h.hexdigest())


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
