# -*- coding: utf-8 -*-

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from .importers.nosdeputes import NosDeputesImporter
from .importers.etapes import EtapesImporter

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
def import_etapes():
    """Crée ou met à jour la liste des étapes"""
    app.config.update(SQLALCHEMY_ECHO=False)
    EtapesImporter(app).run()

@manager.command
def import_nd():
    """Importe les députés depuis NosDéputés.fr"""
    app.config.update(SQLALCHEMY_ECHO=False)
    NosDeputesImporter(app).run()
