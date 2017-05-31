# -*- coding: utf-8 -*-

from flask import render_template

from ..models.constants import ETAPES_BY_ORDRE
from ..models.queries import par_etape, par_departement, random_parl


def setup_routes(app):

    @app.route('/', endpoint='home')
    def home():
        etapes_qs = par_etape()

        def each_etape(getter):
            return [getter(e) for e in etapes_qs]

        def key_each_etape(key):
            return each_etape(lambda e: ETAPES_BY_ORDRE[e.etape][key])

        etapes_data = {
            'labels': key_each_etape('label'),
            'datasets': [{
                'data': each_etape(lambda e: e.nb),
                'backgroundColor': key_each_etape('couleur'),
                'hoverBackgroundColor': key_each_etape('couleur'),
                'borderWidth': each_etape(lambda e: 0)
            }]
        }

        return render_template(
            'index.html.j2',
            parlementaire=random_parl(),
            etapes_data=etapes_data,
            departements=par_departement()
        )
