# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup

import requests

from .base import BaseImporter
from ..models import Action, Parlementaire, db
from ..models.constants import ETAPE_ENVOYE


class LaPosteImporter(BaseImporter):

    URL = 'http://www.part.csuivi.courrier.laposte.fr/suivi/index?id={}'
    cache = {}

    def _next_el_sibling(self, soup):
        cur = soup
        while cur and cur.next_sibling and cur.next_sibling.name is None:
            cur = cur.next_sibling
        return cur.next_sibling

    def _import_suivi(self, suivi):
        self.info('Recherche suivi %s' % suivi)

        url = self.URL.format(suivi)
        try:
            soup = BeautifulSoup(requests.get(url).content, 'html5lib')
        except Exception as e:
            self.error('Erreur sur %s: %s' % (url, e))
            return None

        ident = soup.select('td.identifiant_num')
        if not len(ident):
            return None

        ident = ident[0]
        if ident.text.strip().startswith('Aucun '):
            return None

        produit = self._next_el_sibling(ident)
        date = self._next_el_sibling(produit)
        localisation = self._next_el_sibling(date)
        statut = self._next_el_sibling(localisation)

        if date and statut:
            return '%s (%s)' % (statut.text, date.text)
        else:
            return None

    def import_suivi(self, suivi):
        if suivi not in self.cache:
            statut = self._import_suivi(suivi)
            self.info('SUIVI %s => %s' % (suivi, statut))

            self.cache[suivi] = statut
        return self.cache[suivi]

    def run(self):
        self.info('Début import suivi depuis La Poste')

        acts = Action.query.join(Action.parlementaire) \
                           .filter(Parlementaire.etape == ETAPE_ENVOYE) \
                           .filter(Action.etape == ETAPE_ENVOYE) \
                           .filter(~Action.suivi.like('%:Distribué%')) \
                           .order_by(Action.suivi) \
                           .all()

        for act in acts:
            if not act.suivi:
                self.error('Pas de suivi: action %s' % act.id)
                continue
            suivi = act.suivi.split(':', 1)[0]
            status = self.import_suivi(suivi)
            if status:
                act.suivi = '%s:%s' % (suivi, status)

        db.session.commit()

        self.info('Import suivi terminé')
