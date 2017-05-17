# -*- coding: utf-8 -*-

import re

from flask import url_for

from jinja2 import Markup, escape, evalcontextfilter


def setup(app):

    @app.template_filter('titre_parlementaire')
    def titre_parlementaire(parl):
        if parl.sexe == 'F':
            return 'Madame la %s' % ('Sénatrice' if parl.chambre == 'SEN'
                                     else 'Députée')
        else:
            return 'Monsieur le %s' % ('Sénateur' if parl.chambre == 'SEN'
                                       else 'Député')

    @app.template_filter('fonc_parlementaire')
    def fonc_parlementaire(parl, article=False):
        if parl.sexe == 'F':
            return 'Sénatrice' if parl.chambre == 'SEN' else 'Députée'
        else:
            return 'Sénateur' if parl.chambre == 'SEN' else 'Député'

    @app.template_filter('lien_parl')
    def lien_parl(parl):
        if parl.chambre == 'AN':
            site = 'de l\'Assemblée nationale'
        else:
            site = 'du Sénat'

        data = (site, parl.url_off,
                url_for('static', filename=parl.chambre.lower() + '.png'))

        return ('<a title="Accéder à la page du parlementaire sur le %s" '
                'data-toggle="tooltip" target="_blank" href="%s">'
                '<img class="chamber-icon" src="%s">'
                '</a>' % data)

    @app.template_filter('lien_rc')
    def lien_rc(parl):
        if parl.chambre == 'AN':
            site = 'NosDéputés.fr'
            icon = 'nd'
        else:
            site = 'NosSénateurs.fr'
            icon = 'ns'

        data = (site, parl.url_rc, url_for('static', filename=icon + '.png'))

        return ('<a title="Accéder à la page du parlementaire sur %s" '
                'data-toggle="tooltip" target="_blank" href="%s">'
                '<img class="chamber-icon" src="%s">'
                '</a>' % data)

    @app.template_filter('label_groupe')
    def label_groupe(groupe):
        return '<span title="%s" class="label" ' \
            'data-toggle="tooltip" ' \
            'style="background-color: %s;">%s</span>' % (
                groupe.nom, groupe.couleur, groupe.sigle
            )

    @app.template_filter('label_etape')
    def label_etape(etape):
        if isinstance(etape, dict):
            data = (etape['description'], etape['couleur'], etape['icone'],
                    etape['label'])
        else:
            data = (etape.description, etape.couleur, etape.icone, etape.label)

        return '<span class="label" title="%s" ' \
            'data-toggle="tooltip" ' \
            'style="background-color: %s;"><i class="fa fa-%s"></i> ' \
            '%s</span>' % data

    @app.template_filter('label_etape_text')
    def label_etape_text(etape):
        if isinstance(etape, dict):
            data = (etape['icone'], etape['label'])
        else:
            data = (etape.icone, etape.label)

        return '<span data-toggle="tooltip"><i class="fa fa-%s"></i> ' \
            '%s</span>' % data

    _paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

    @app.template_filter('nl2br')
    @evalcontextfilter
    def nl2br(eval_ctx, value):
        result = u'\n\n'.join(u'%s' % p.replace('\n', '<br>\n')
                              for p in _paragraph_re.split(escape(value)))
        if eval_ctx.autoescape:
            result = Markup(result)
        return result
