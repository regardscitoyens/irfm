# -*- coding: utf-8 -*-

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
            'style="background-color: %s;">%s</span>' % (
                groupe.nom, groupe.couleur, groupe.sigle
            )
