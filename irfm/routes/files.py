# -*- coding: utf-8 -*-

import os

from flask import redirect, send_from_directory, url_for

from ..models import Action, Etape, Parlementaire
from ..models.constants import ETAPE_ENVOYE

from ..tools.files import generer_demande
from ..tools.routing import not_found


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
        return redirect(url_for('get_file', filename=filename))

    @app.route('/parlementaire/<id>/preuve-envoi', endpoint='preuve_envoi')
    def preuve_envoi(id):
        act = Action.query.join(Action.etape) \
                          .filter(Etape.ordre == ETAPE_ENVOYE,
                                  Action.parlementaire_id == id) \
                          .first()

        if not act or not act.attachment:
            return not_found()

        return redirect(url_for('get_upload', filename=act.attachment,
                                _external=True))

    @app.route('/parlementaire/attachment/<id>', endpoint='attachment')
    def attachment(id):
        act = Action.query.filter_by(id=id).first()

        if not act or not act.attachment:
            return not_found()

        return redirect(url_for('get_upload', filename=act.attachment,
                                _external=True))

    @app.route('/files/<filename>', endpoint='get_file')
    def get_file(filename):
        return send_from_directory(files_root, filename)

    @app.route('/uploads/<filename>', endpoint='get_upload')
    def get_upload(filename):
        return send_from_directory(uploads_root, filename)
