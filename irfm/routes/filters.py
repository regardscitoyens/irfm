# -*- coding: utf-8 -*-

import re

from jinja2 import evalcontextfilter, Markup, escape


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
    def fonc_parlementaire(parl):
        if parl.sexe == 'F':
            return 'Sénatrice' if parl.chambre == 'SEN' else 'Députée'
        else:
            return 'Sénateur' if parl.chambre == 'SEN' else 'Député'

    @app.template_filter('label_groupe')
    def label_groupe(groupe):
        return '<span title="%s" class="label" ' \
            'data-toggle="tooltip" ' \
            'style="background-color: %s;">%s</span>' % (
                groupe.nom, groupe.couleur, groupe.sigle
            )

    @app.template_filter('label_etape')
    def label_etape(etape):
        return '<span class="label" title="%s" ' \
            'data-toggle="tooltip" ' \
            'style="background-color: %s;"><i class="fa fa-%s"></i> ' \
            '%s</span>' % (
                etape.description, etape.couleur, etape.icone, etape.label
            )

    _paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

    @app.template_filter('nl2br')
    @evalcontextfilter
    def nl2br(eval_ctx, value):
        result = u'\n\n'.join(u'%s' % p.replace('\n', '<br>\n')
                              for p in _paragraph_re.split(escape(value)))
        if eval_ctx.autoescape:
            result = Markup(result)
        return result
