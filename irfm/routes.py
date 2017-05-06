# -*- coding: utf-8 -*-

from flask import abort, render_template, url_for
from sqlalchemy.orm import joinedload, contains_eager
from sqlalchemy.sql.expression import func

from .models import db, Etape, Parlementaire


def setup_routes(app):

    @app.context_processor
    def inject_piwik():
        piwik = None
        if app.config['PIWIK_HOST']:
            piwik = {
                'host': app.config['PIWIK_HOST'],
                'id': app.config['PIWIK_ID']
            }

        return {'piwik':piwik}

    @app.context_processor
    def inject_menu():
        return {
            'menu': [
                {
                    'url': url_for('home'),
                    'label': 'Accueil',
                    'endpoint': 'home',
                },
                {
                    'url': url_for('parlementaires'),
                    'label': 'Liste des parlementaires',
                    'endpoint': 'parlementaires',
                },
            ]
        }

    @app.template_filter('titre_parlementaire')
    def titre_parlementaire(parl):
        if parl.sexe == 'F':
            return 'Madame la %s' % ('Sénatrice' if parl.chambre == 'SEN'
                                                 else 'Députée')
        else:
            return 'Monsieur le %s' % ('Sénateur' if parl.chambre == 'SEN'
                                                  else 'Député')

    @app.template_filter('fonc_parlementaire')
    def fonc_parlementaire(parl):
        if parl.sexe == 'F':
            return 'Sénatrice' if parl.chambre == 'SEN' else 'Députée'
        else:
            return 'Sénateur' if parl.chambre == 'SEN' else 'Député'

    @app.template_filter('label_groupe')
    def label_groupe(groupe):
        return '<span title="%s" class="label" ' \
            'style="background-color: %s;">%s</span>' % (
                groupe.nom, groupe.couleur, groupe.sigle
            )

    @app.route('/', endpoint='home')
    def home():
        pqs = Parlementaire.query.options(joinedload(Parlementaire.etape)) \
                                 .filter(Etape.label == 'À envoyer') \
                                 .order_by(func.random())

        eqs = db.session.query(Etape) \
                        .outerjoin(Etape.parlementaires) \
                        .add_columns(func.count(Parlementaire.id)
                                         .label('nb')) \
                        .filter(Etape.ordre > 0) \
                        .group_by(Etape) \
                        .order_by(Etape.ordre) \
                        .all()

        return render_template(
            'index.html.j2',
            parlementaire=pqs.first(),
            etapes=[e.Etape for e in eqs],
            etapes_data={
                'labels': [e.Etape.label for e in eqs],
                'datasets': [{
                    'data': [e.nb for e in eqs],
                    'backgroundColor': [e.Etape.couleur for e in eqs]
                }]
            }
        )

    @app.route('/parlementaires', endpoint='parlementaires')
    def parlementaires():
        qs = Parlementaire.query.join(Parlementaire.etape) \
                                .options(joinedload(Parlementaire.groupe)) \
                                .options(contains_eager(Parlementaire.etape)) \
                                .filter(Etape.ordre > 0) \
                                .all()

        return render_template(
            'list.html.j2',
            parlementaires=qs
        )

    @app.route('/parlementaires/<id>', endpoint='parlementaire')
    def parlementaire(id):
        parl = Parlementaire.query.filter_by(id=id) \
                                  .options(joinedload(Parlementaire.groupe)) \
                                  .options(joinedload(Parlementaire.etape)) \
                                  .first()

        if not parl:
            abort(404)

        return render_template(
            'parlementaire.html.j2',
            parlementaire=parl
        )

    @app.route('/parlementaires/<id>/demande', endpoint='demande')
    def demande(id):
        parl = Parlementaire.query.filter_by(id=id).first()

        if not parl:
            abort(404)

        return render_template(
            'demande.html.j2',
            parlementaire=parl
        )
