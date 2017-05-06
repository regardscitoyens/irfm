# -*- coding: utf-8 -*-

from flask import abort, make_response, render_template
from xhtml2pdf import pisa
from io import BytesIO

from ..models import Parlementaire


def setup_routes(app):

    @app.route('/demande/<id>', endpoint='demande_pdf')
    def demande_pdf(id):
        parl = Parlementaire.query.filter_by(id=id).first()

        if not parl:
            abort(404)

        html = render_template('demande.html.j2',
            parlementaire=parl
        )



        pdf = BytesIO()
        pisa.CreatePDF(html, pdf)
        response = make_response(pdf.getvalue())
        pdf.close()

        response.headers['Content-Type'] = 'application/pdf'
        return response
