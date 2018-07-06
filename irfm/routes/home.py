# -*- coding: utf-8 -*-

from flask import render_template

from ..models.constants import ETAPES_BY_ORDRE, ETAPE_DEMANDE_CADA
from ..models.queries import (
    etat_courriers,
    par_etape,
    par_departement,
    random_parl,
    current_step,
    nb_ok,
    nb_ko,
)


def setup_routes(app):
    @app.route("/", endpoint="home")
    def home():
        step = current_step()

        kwargs = dict(
            parlementaire=random_parl(), current_step=step, nb_ok=nb_ok(), nb_ko=nb_ko()
        )

        if step < ETAPE_DEMANDE_CADA:
            # Données camembert

            etapes_qs = par_etape()

            def each_etape(getter):
                return [getter(e) for e in etapes_qs]

            def key_each_etape(key):
                return each_etape(lambda e: ETAPES_BY_ORDRE[e.etape][key])

            kwargs["etapes_data"] = {
                "labels": key_each_etape("label"),
                "datasets": [
                    {
                        "data": each_etape(lambda e: e.nb),
                        "backgroundColor": key_each_etape("couleur"),
                        "hoverBackgroundColor": key_each_etape("couleur"),
                        "borderWidth": 0,
                    }
                ],
            }

            # Données histogramme

            etats = etat_courriers()
            kwargs["histo_data"] = {
                "labels": [etat for etat, nb in etats],
                "datasets": [{"data": [nb for etat, nb in etats]}],
            }

            kwargs["departements"] = par_departement()

        return render_template("index.html.j2", **kwargs)
