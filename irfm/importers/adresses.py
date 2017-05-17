# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup

import requests

from .base import BaseImporter
from ..models import Etape, Parlementaire, db
from ..models.constants import ETAPE_NA


ADRESSES_OVERRIDE = {
    "Sylvie Andrieux": [
        "Permanence parlementaire",
        "1 Place Albert Durand",
        "Village de Sainte-Marthe",
        "13014 Marseille"
    ],
    # "Eric Bothorel": [
    # ],
    "Christophe Caresche": [
        "Permanence parlementaire",
        "76 Bis Rue Duhesme",
        "75018 Paris"
    ],
    "Carlos Da Silva": [
        "35 Bis Rue Féray",
        "91100 Corbeil-Essonnes"
    ],
    # "Monique Lubin": [
    # ],
    "Christophe Premat": [
        "Assemblée nationale",
        "126 Rue de l'Université",
        "75355 Paris 07 S"
    ],
    "Pascal Terrasse": [
        "11 Avenue de Coux",
        "07000 Privas"
    ],
    "Yannick Trigance": [
        "Permanence parlementaire",
        "19 Rue Charles Schmidt",
        "93400 Saint-Ouen"
    ],
}


class AdressesImporter(BaseImporter):
    def import_adresse(self, parl):
        if parl.nom_complet in ADRESSES_OVERRIDE:
            lines = ADRESSES_OVERRIDE[parl.nom_complet]
        else:
            if 'assemblee-nationale' not in parl.url_off:
                return False

            soup = BeautifulSoup(requests.get(parl.url_off).text, 'html5lib')
            adrs = [a for a in soup.select('dl.adr')
                    if 'Assemblée nationale' in a.text or
                    'En circonscription' in a.text]

            if not len(adrs):
                return False

            adr = adrs[-1]

            try:
                lines = [e.text.strip()
                         for e in adr.select('.street-address')] + \
                        ['%s %s' % (adr.select('.postal-code')[0].text.strip(),
                         adr.select('.locality')[0].text.strip())]
            except Exception as e:
                self.error('Erreur sur %s: %s' % (parl.url_off, e))
                return False

        parl.adresse = '\n'.join(lines)
        db.session.commit()

        return True

    def run(self):
        self.info('Début import adresses')
        qs = Parlementaire.query.join(Parlementaire.etape) \
                                .filter(Etape.ordre > ETAPE_NA) \
                                .filter(Parlementaire.adresse is None) \
                                .order_by(Parlementaire.nom) \
                                .all()

        self.info('%s parlementaires concernés sans adresse' % len(qs))

        missing = []
        for parl in qs:
            found = self.import_adresse(parl)
            if not found:
                missing.append(parl.nom_complet)

        if len(missing):
            self.info('Parlementaires concernés restant sans adresse: %s'
                      % ', '.join(missing))

        self.info('Import adresses terminé')
