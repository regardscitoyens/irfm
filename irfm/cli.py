# -*- coding: utf-8 -*-

import os
from getpass import getpass

from flask_migrate import Migrate, MigrateCommand

from flask_script import Manager

from .importers.adresses import AdressesImporter
from .importers.emails import EmailImporter
from .importers.laposte import LaPosteImporter
from .importers.nosdeputes import NosDeputesImporter

from .irfm import app

from .models import db

from .tools.files import generer_demandes as generer_demandes_
from .tools.mails import (envoyer_emails as envoyer_emails_,
                          envoyer_relances as envoyer_relances_,
                          mailing_lists as mailing_lists_,
                          erratum_cada as erratum_cada_,
                          extraire_mails_cada as extraire_mails_cada_)
from .tools.procedure import (fix_procedure as fix_procedure_,
                              avance_procedure as avance_procedure_,
                              export_pour_ta as export_pour_ta_)
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
@manager.option('--modele', dest='modele', default=None)
def envoyer_emails(envoyer=False, modele=None):
    """Envoie des e-mails pour tous les parlementaires"""
    app.config.update(SQLALCHEMY_ECHO=False)
    missed_addr, missed_email = envoyer_emails_(app, envoyer, modele)

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
@manager.option('--envoyer', action='store_true')
def envoyer_relances(envoyer=False):
    """Envoie des e-mails de relance"""
    app.config.update(SQLALCHEMY_ECHO=False)
    envoyer_relances_(app, envoyer)


@manager.command
def mailing_lists():
    """Affiche les abonnés aux mailing lists"""
    app.config.update(SQLALCHEMY_ECHO=False)
    for nom, emails in mailing_lists_().items():
        print('%s :\n\t%s' % (nom, '\n\t'.join(emails)))


@manager.command
def fix_procedure():
    """Génère les étapes manquantes pour tous les parlementaires"""
    app.config.update(SQLALCHEMY_ECHO=False)
    fix_procedure_(app)


@manager.command
def export_pour_ta():
    """Génère un export CSV pour les requêtes TA"""
    app.config.update(SQLALCHEMY_ECHO=False)
    export_pour_ta_(app)


@manager.command
@manager.option('-e', '--etape', dest='etape', default=None)
def avance_procedure(etape):
    """
    Avance la procédure pour tous les parlementaire, et envoie les alertes
    correspondantes.
    """
    app.config.update(SQLALCHEMY_ECHO=False)
    avance_procedure_(app, int(etape))


@manager.command
def erratum_cada():
    """
    Envoi les e-mails d'erratum CADA
    """
    app.config.update(SQLALCHEMY_ECHO=False)
    erratum_cada_(app)


@manager.command
def extraire_mails_cada():
    """
    Extraire les e-mails de réponse CADA
    """
    app.config.update(SQLALCHEMY_ECHO=False)
    extraire_mails_cada_(app)


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
def import_laposte():
    """Importe l'état des courriers suivi depuis La Poste"""
    app.config.update(SQLALCHEMY_ECHO=False)
    LaPosteImporter(app).run()


@manager.command
def import_emails():
    """
    Importe les emails des députés depuis un fichier DATA_DIR/emails.csv au
    format "nom complet;email1,email2,..."
    """
    app.config.update(SQLALCHEMY_ECHO=False)
    EmailImporter(app).run()


@manager.command
def password():
    """Chiffre un mot de passe admin"""
    print(hash_password(getpass(), app.config['SECRET_KEY']))


@manager.command
def runserver():
    """Exécute le serveur web flask intégré"""
    app.run()
