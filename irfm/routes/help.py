# -*- coding: utf-8 -*-

from flask import render_template


def setup_routes(app):

    @app.route('/faq', endpoint='faq')
    def faq():
        return render_template('markdown.html.j2',
                               title='Foire aux Questions',
                               file='text/FAQ.md')

    @app.route('/historique', endpoint='historique')
    def historique():
        return render_template('markdown.html.j2',
                               title='Qu\'est-ce que l\'IRFM ?',
                               file='text/historique.md')

    @app.route('/derives', endpoint='derives')
    def derives():
        return render_template('markdown.html.j2',
                               title='Les dérives de l\'IRFM',
                               file='text/derives.md')

    @app.route('/aide/papier', endpoint='tuto_papier')
    def tuto_papier():
        return render_template('markdown.html.j2',
                               title='Envoyer un recommander papier',
                               file='text/tuto_papier.md')

    @app.route('/aide/enligne', endpoint='tuto_enligne')
    def tuto_enligne():
        return render_template('markdown.html.j2',
                               title='Envoyer un recommander en ligne',
                               file='text/tuto_enligne.md')
