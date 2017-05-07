# -*- coding: utf-8 -*-

from io import BytesIO

from flask import abort, make_response, render_template
from xhtml2pdf import pisa

from .util import not_found, slugify
from ..models import Parlementaire



def setup_routes(app):

    @app.route('/parlementaire/<id>/demande/<mode>', endpoint='demande_pdf')
    def demande_pdf(id, mode='download'):
        parl = Parlementaire.query.filter_by(id=id).first()

        if not parl:
            return not_found()

        slug = slugify(parl.nom_complet)

        html = render_template('demande.html.j2',
            parlementaire=parl
        )

        pdf = BytesIO()
        pisa.CreatePDF(html, pdf)
        response = make_response(pdf.getvalue())
        pdf.close()

        response.headers['Content-Type'] = 'application/pdf'
        if mode == 'download':
            response.headers['Content-Disposition'] = \
                'attachment; filename="courrier-irfm-%s.pdf"' % slug

        return response
