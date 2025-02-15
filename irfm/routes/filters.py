# -*- coding: utf-8 -*-

import re

from flask import url_for

from jinja2 import Markup, escape, evalcontextfilter

from ..models.constants import ETAPES_BY_ORDRE


def setup(app):

    @app.template_filter('si_sexe')
    def si_sexe(parl, si_femme, si_homme):
        return si_femme if parl.sexe == 'F' else si_homme

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
            return 'Sénatrice' if parl.chambre == 'SEN' else 'Députée entre 2012 et 2017'
        else:
            return 'Sénateur' if parl.chambre == 'SEN' else 'Député entre 2012 et 2017'

    @app.template_filter('lien_parl')
    def lien_parl(parl):
        if parl.chambre == 'AN':
            site = 'de l\'Assemblée nationale'
        else:
            site = 'du Sénat'

        data = (site, parl.url_off,
                url_for('static', filename=parl.chambre.lower() + '.png'))

        return ('<a title="Accéder à la page du parlementaire sur le site '
                ' %s" data-toggle="tooltip" target="_blank" href="%s">'
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

    @app.template_filter('hashtag_circo')
    def hashtag_circo(parl):
        return '#Circo%s' % parl.num_deptmt

    @app.template_filter('label_groupe')
    def label_groupe(groupe):
        return '<span title="%s" class="label" ' \
            'data-toggle="tooltip" ' \
            'style="background-color: %s;">%s</span>' % (
                groupe.nom, groupe.couleur, groupe.sigle
            )

    @app.template_filter('label_etape')
    def label_etape(etape):
        if isinstance(etape, int):
            etape = ETAPES_BY_ORDRE[etape]

        return ('<span class="label" title="%(description)s" '
                'data-toggle="tooltip" style="background-color: %(couleur)s;">'
                '<i class="fa fa-%(icone)s"></i> %(label)s</span>') % etape

    @app.template_filter('label_etape_text')
    def label_etape_text(etape):
        if isinstance(etape, int):
            etape = ETAPES_BY_ORDRE[etape]

        return ('<span data-toggle="tooltip"><i class="fa fa-%(icone)s"></i> '
                '%(label)s</span>') % etape

    @app.template_filter('suivi_laposte')
    def suivi_laposte(suivi):
        if not suivi:
            return ''

        parts = suivi.split(':', 1)
        link = 'http://www.part.csuivi.courrier.laposte.fr/suivi/index?id=%s' \
               % parts[0]
        html = 'Suivi&nbsp: <a href="%s" target="_blank">%s</a>' \
               % (link, parts[0])

        if len(parts) > 1:
            html += ' <span class="anon">&ndash; %s</span>' % parts[1]

        warning = 'Le suivi peut ne pas fonctionner avant 24 heures.'
        html += '<br><small>%s</small>' % warning

        return html

    _paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

    @app.template_filter('nl2br')
    @evalcontextfilter
    def nl2br(eval_ctx, value):
        result = u'\n\n'.join(u'%s' % p.replace('\n', '<br>\n')
                              for p in _paragraph_re.split(escape(value)))
        if eval_ctx.autoescape:
            result = Markup(result)
        return result

    @app.template_filter('image_tuto')
    def image_tuto(filename):
        url = url_for('static', filename=filename)

        return ('<div class="well tuto-image">'
                '<a target="_blank" href="%s">'
                '<img src="%s">'
                '</a>'
                '</div>') % (url, url)
