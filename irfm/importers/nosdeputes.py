# -*- coding: utf-8 -*-

from datetime import datetime

import dateparser
import requests
from sqlalchemy.inspection import inspect

from ..models import db, Parlementaire


def parse_date(date):
    if not date:
        return None
    elif len(date) >= 19:
        return dateparser.parse(date[0:19])
    else:
        return dateparser.parse(date[0:10])


class NosDeputesImporter(object):

    URL_LISTE = 'https://www.nosdeputes.fr/deputes/json'
    URL_PHOTO = '//www.nosdeputes.fr/depute/photo/%(slug)s'

    columns = None

    def __init__(self, app):
        self.app = app

    def info(self, msg):
        self.app.logger.info(u'<%s> %s' % (self.__class__.__name__, msg))

    def error(self, msg):
        self.app.logger.error(u'<%s> %s' % (self.__class__.__name__, msg))

    def import_depute(self, data):
        if not self.columns:
            mapper = inspect(Parlementaire)
            self.columns = {c.name: type(c.type).__name__
                            for c in mapper.columns}
        cols = self.columns

        created = False
        updated = False
        id_data = {
            'chambre': 'AN',
            'nom': data['nom_de_famille'],
            'prenom': data['prenom'],
        }

        depute = Parlementaire.query.filter_by(**id_data).first()

        if not depute:
            id_data.update({'etape': 'NOUVEAU'})
            depute = Parlementaire(**id_data)
            db.session.add(depute)
            created = True

        fields = {
            'sexe': data['sexe'],

            'mandat_debut': parse_date(data['mandat_debut']),
            'mandat_fin': parse_date(data.get('mandat_fin', None)),
            'num_deptmt': data['num_deptmt'],
            'nom_circo': data['nom_circo'],
            'num_circo': data['num_circo'],
            'groupe': data['parti_ratt_financier'],
            'groupe_sigle': data['groupe_sigle'],

            'url_photo': self.URL_PHOTO % data,
            'url_rc': data['url_nosdeputes'],
            'url_off': data['url_an'],
        }

        for key, newvalue in fields.items():
            curvalue = getattr(depute, key)

            if key in cols:
                if cols[key] == 'Date' and isinstance(newvalue, datetime):
                    newvalue = newvalue.date()

            if curvalue != newvalue:
                updated = True
                setattr(depute, key, newvalue)

        return created, updated

    def run(self):
        self.info('Début import NosDéputés.fr')

        try:
            data = requests.get(self.URL_LISTE).json()
        except Exception as e:
            self.error('Téléchargement %s impossible: %s' % (URL_LISTE, e))
            return

        self.info('%s députés trouvés' % len(data['deputes']))

        created = 0
        updated = 0

        for depute in data['deputes']:
            c, u = self.import_depute(depute['depute'])
            if c:
                created += 1
            elif u:
                updated += 1

        db.session.commit()
        db.session.flush()

        self.info('Import terminé: %s créés, %s mis à jour' % (created,
                                                               updated))
