# -*- coding: utf-8 -*-

from io import BytesIO
import re
import unicodedata

from flask import abort, make_response, render_template
from xhtml2pdf import pisa

from ..models import Parlementaire


SLUG_STRIP_RE = re.compile(r'[^\w\s-]')
SLUG_HYP_RE = re.compile(r'[-\s]+')

def slugify(value):
    if not isinstance(value, str):
        value = str(value)
    value = str(unicodedata.normalize('NFKD', value).encode('ascii', 'ignore'))
    value = str(SLUG_STRIP_RE.sub('', value).strip().lower())
    value = SLUG_HYP_RE.sub('-', value)

    return value[1:]


def setup_routes(app):

    @app.route('/demande/<id>/<mode>', endpoint='demande_pdf')
    def demande_pdf(id, mode='download'):
        parl = Parlementaire.query.filter_by(id=id).first()

        if not parl:
            abort(404)

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
