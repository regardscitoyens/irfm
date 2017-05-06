# -*- coding: utf-8 -*-

from .base import BaseImporter
from ..models import db, Etape
from ..models.constants import ETAPES


class EtapesImporter(BaseImporter):

    def import_etape(self, data):
        created = False
        updated = False

        id_data = {'ordre': data['ordre']}

        etape = Etape.query.filter_by(**id_data).first()

        if not etape:
            etape = Etape(**id_data)
            db.session.add(etape)
            created = True

        for key, newvalue in data.items():
            if key == 'ordre':
                continue

            curvalue = getattr(etape, key)

            if curvalue != newvalue:
                updated = True
                setattr(etape, key, newvalue)

        return created, updated


    def run(self):
        self.info('Début import étapes')

        self.info('%s étapes trouvés' % len(ETAPES))

        created = 0
        updated = 0

        for etape in ETAPES:
            c, u = self.import_etape(etape)
            if c:
                created += 1
            elif u:
                updated += 1

        db.session.commit()

        self.info('Import étapes terminé: %s créées, %s mises à jour'
                  % (created, updated))
