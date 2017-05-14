# -*- coding: utf-8 -*-

from io import BytesIO
import os

from flask import make_response, render_template, send_file

from ..models import Action, Etape, Parlementaire
from ..models.constants import ETAPE_ENVOYE

from ..tools.files import EXTENSIONS, generer_demande
from ..tools.routing import not_found
from ..tools.text import slugify


def setup_routes(app):
    files_root = os.path.join(app.config['DATA_DIR'], 'files')
    if not os.path.exists(files_root):
        os.mkdir(files_root)

    uploads_root = os.path.join(app.config['DATA_DIR'], 'uploads')
    if not os.path.exists(uploads_root):
        os.mkdir(uploads_root)

    @app.route('/parlementaire/<id>/demande/<mode>', endpoint='demande_pdf')
    def demande_pdf(id, mode='download'):
        parl = Parlementaire.query.filter_by(id=id).first()

        if not parl:
            return not_found()

        filename = generer_demande(parl, files_root)

        attach = None
        if mode == 'download':
            attach = os.path.basename(filename)

        return send_file(
            path,
            mimetype='application/pdf',
            conditional=True,
            as_attachment=bool(attach),
            attachment_filename=attach
        )

    @app.route('/parlementaire/<id>/preuve-envoi', endpoint='preuve_envoi')
    def preuve_envoi(id):
        act = Action.query.join(Action.etape) \
                          .filter(Etape.ordre == ETAPE_ENVOYE,
                                  Action.parlementaire_id == id) \
                          .first()

        if not act or not act.attachment:
            return not_found()

        path = os.path.join(uploads_root, act.attachment)
        ext = path.rsplit('.', 1)[1].lower()

        return send_file(
            path,
            mimetype=EXTENSIONS[ext],
            conditional=True,
        )

    @app.route('/parlementaire/document/<id>', endpoint='document')
    def document(id):
        act = Action.query.filter_by(id=id).first()

        if not act or not act.attachment:
            return not_found()

        path = os.path.join(uploads_root, act.attachment)
        ext = path.rsplit('.', 1)[1].lower()

        return send_file(
            path,
            mimetype=EXTENSIONS[ext],
            conditional=True,
        )
