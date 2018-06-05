# -*- coding: utf-8 -*-

import csv
from os.path import join

from .base import BaseImporter
from ..models import Parlementaire, db


class NonTrouve(Exception):
    pass


class EmailImporter(BaseImporter):

    def import_emails(self, nom, emails):
        parl = Parlementaire.query.filter(Parlementaire.nom_complet == nom) \
                                  .one()
        if not parl:
            raise NonTrouve('%s non trouvé' % nom)

        if parl.emails != emails:
            self.info('%s => %s' % (nom, emails))
            parl.emails = emails
            db.session.commit()
            return True

        return False

    def run(self):
        self.info('Début import emails')

        erreurs = 0
        changes = 0
        with open(join(self.app.config['DATA_DIR'], 'emails.csv'),
                  newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                try:
                    if self.import_emails(row['nom'], row['emails']):
                        changes = changes + 1
                except NonTrouve:
                    self.error('Non trouvé: %s' % row['nom'])
                    erreurs = erreurs + 1

        self.info('Import emails terminé, %s changements, %s erreurs' %
                  (changes, erreurs))
