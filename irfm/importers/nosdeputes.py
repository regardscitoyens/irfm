# -*- coding: utf-8 -*-

from datetime import datetime

import dateparser
import requests
from sqlalchemy.inspection import inspect

from .base import BaseImporter
from ..models import db, Etape, Groupe, Parlementaire


def parse_date(date):
    if not date:
        return None
    elif len(date) >= 19:
        return dateparser.parse(date[0:19])
    else:
        return dateparser.parse(date[0:10])


def dechex(dec):
    s = hex(int(dec))[2:]
    if len(s) == 1:
        s = '0' + s
    elif len(s) > 2:
        s = 'ff'
    return s


def parse_couleur(couleur):
    if not couleur:
        return '#000000'
    else:
        return '#' + ''.join(map(dechex, couleur.split(',')))


class NosDeputesImporter(BaseImporter):

    URL_GROUPES = 'https://www.nosdeputes.fr/organismes/groupe/json'
    URL_DEPUTES = 'https://www.nosdeputes.fr/deputes/json'
    URL_PHOTO = '//www.nosdeputes.fr/depute/photo/%(slug)s'
    DATE_DEBUT = parse_date('2017-01-01')

    columns = None
    groupes = {}

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
            id_data.update({'etape': self.etape_nv})
            depute = Parlementaire(**id_data)
            db.session.add(depute)
            created = True

        fields = {
            'sexe': data['sexe'],
            'nom_complet': data['nom'],

            'mandat_debut': parse_date(data['mandat_debut']),
            'mandat_fin': parse_date(data.get('mandat_fin', None)),
            'num_deptmt': data['num_deptmt'],
            'nom_circo': data['nom_circo'],
            'num_circo': data['num_circo'],

            'groupe': self.groupes[data['groupe_sigle'] or 'NI'],

            'url_photo': self.URL_PHOTO % data,
            'url_rc': data['url_nosdeputes'],
            'url_off': data['url_an'],
        }

        if fields['mandat_fin'] and fields['mandat_fin'] < self.DATE_DEBUT:
            fields['etape'] = self.etape_na

        for key, newvalue in fields.items():
            curvalue = getattr(depute, key)

            if key in cols:
                if cols[key] == 'Date' and isinstance(newvalue, datetime):
                    newvalue = newvalue.date()

            if curvalue != newvalue:
                updated = True
                setattr(depute, key, newvalue)

        return created, updated

    def import_deputes(self):
        self.etape_na = Etape.query.filter_by(label='N/A').first()
        if not self.etape_na:
            self.error('Etape N/A introuvable, exécuter import_etapes ?')
            return

        self.etape_nv = Etape.query.filter_by(label='À envoyer').first()
        if not self.etape_nv:
            self.error('Etape À envoyer introuvable, exécuter import_etapes ?')
            return

        try:
            data = requests.get(self.URL_DEPUTES).json()
        except Exception as e:
            self.error('Téléchargement %s impossible: %s' % (URL_DEPUTES, e))
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

        self.info('Import députés terminé: %s créés, %s mis à jour'
                  % (created, updated))

    def import_groupe(self, data):
        created = False
        updated = False

        if data.get('acronyme', None):
            id_data = {
                'chambre': 'AN',
                'sigle': data['acronyme']
            }

            groupe = Groupe.query.filter_by(**id_data).first()

            if not groupe:
                groupe = Groupe(**id_data)
                db.session.add(groupe)
                created = True

            self.groupes[id_data['sigle']] = groupe

            fields = {
                'nom': data['nom'],
                'couleur': parse_couleur(data['couleur'])
            }

            for key, newvalue in fields.items():
                curvalue = getattr(groupe, key)

                if curvalue != newvalue:
                    updated = True
                    setattr(groupe, key, newvalue)

        return created, updated

    def import_groupes(self):
        try:
            data = requests.get(self.URL_GROUPES).json()
        except Exception as e:
            self.error('Téléchargement %s impossible: %s' % (URL_DEPUTES, e))
            return

        self.info('%s organismes trouvés' % len(data['organismes']))

        created = 0
        updated = 0

        for org in data['organismes']:
            c, u = self.import_groupe(org['organisme'])
            if c:
                created += 1
            elif u:
                updated += 1

        db.session.commit()

        self.info('Import groupes terminé: %s créés, %s mis à jour'
                  % (created, updated))

    def run(self):
        self.info('Début import NosDéputés.fr')
        self.import_groupes()
        self.import_deputes()
