# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests

from .base import BaseImporter
from ..models import db, Parlementaire


class AdressesImporter(BaseImporter):
    def import_adresse(self, parl):
        if not 'assemblee-nationale' in parl.url_off:
            return

        soup = BeautifulSoup(requests.get(parl.url_off).text, 'html5lib')
        adrs = [a for a in soup.select('dl.adr')
                if 'Assemblée nationale' in a.text
                or 'En circonscription' in a.text]

        if not len(adrs):
            return

        adr = adrs[-1]

        try:
            lines = [e.text.strip() for e in adr.select('.street-address')] + [
                '%s %s' % (adr.select('.postal-code')[0].text.strip(),
                           adr.select('.locality')[0].text.strip())
            ]
        except Exception as e:
            self.error('Erreur sur %s: %s' % (parl.url_off, e))
            return

        parl.adresse = '\n'.join(lines);
        db.session.commit()

    def run(self):
        self.info('Début import adresses')
        qs = Parlementaire.query.filter_by(adresse=None).all()

        self.info('%s parlementaires sans adresse' % len(qs))

        for parl in qs:
            self.import_adresse(parl)

        self.info('Import adresses terminé')
