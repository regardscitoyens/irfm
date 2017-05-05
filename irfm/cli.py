# -*- coding: utf-8 -*-

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from .irfm import app
from .models import db


manager = Manager(app)
migrate = Migrate(app, db)


manager.add_command('db', MigrateCommand)


@manager.command
def runserver():
    """Exécute le serveur web flask intégré"""
    app.run()

