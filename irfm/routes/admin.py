# -*- coding: utf-8 -*-

import os
from datetime import datetime

from flask import (
    flash,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from sqlalchemy.orm import joinedload

from ..models import Action, Parlementaire, User, db
from ..models.constants import (
    ETAPE_A_CONFIRMER,
    ETAPE_A_ENVOYER,
    ETAPES_BY_ORDRE,
    ETAPE_COM_A_MODERER,
    ETAPE_COM_PUBLIE,
    ETAPE_DOC_MASQUE,
    ETAPE_DOC_PUBLIE,
)

from ..tools.files import EXTENSIONS, handle_upload
from ..tools.mails import envoyer_alerte
from ..tools.routing import not_found, redirect_back, remote_addr, require_admin
from ..tools.text import slugify


def setup_routes(app):
    uploads_root = os.path.join(app.config["DATA_DIR"], "uploads")

    def recent(offset=0):
        qs = (
            Action.query.options(joinedload(Action.parlementaire))
            .options(joinedload(Action.user))
            .order_by(Action.date.desc())
            .offset(offset)
            .limit(100)
            .all()
        )

        return render_template(
            "admin_recent.html.j2", titre="Actions récentes", actions=qs, offset=offset
        )

    @app.route("/admin/recent", endpoint="admin_recent")
    @require_admin
    def admin_recent():
        return recent(0)

    @app.route("/admin/recent/<offset>", endpoint="admin_recent_offset")
    @require_admin
    def admin_recent_offset(offset):
        return recent(int(offset))

    @app.route("/admin/en-attente", endpoint="admin_en_attente")
    @require_admin
    def admin_en_attente():
        # Sous requête des parlementaires à l'étape "à confirmer"
        parls = (
            db.session.query(Parlementaire.id)
            .filter(Parlementaire.etape == ETAPE_A_CONFIRMER)
            .subquery()
        )

        # Actions "à confirmer" pour ces parlementaires
        qs = (
            Action.query.filter(Action.parlementaire_id.in_(parls))
            .filter(Action.etape == ETAPE_A_CONFIRMER)
            .options(joinedload(Action.user))
            .order_by(Action.date)
            .all()
        )

        return render_template(
            "admin_recent.html.j2", titre="Actions en attente", actions=qs
        )

    @app.route("/admin/commentaires", endpoint="admin_commentaires")
    @require_admin
    def admin_commentaires():
        qs = (
            Action.query.filter(Action.etape == ETAPE_COM_A_MODERER)
            .options(joinedload(Action.parlementaire))
            .options(joinedload(Action.user))
            .order_by(Action.date)
            .all()
        )

        return render_template("admin_commentaires.html.j2", actions=qs)

    @app.route("/admin/delete/<id>", endpoint="admin_delete")
    @require_admin
    def admin_delete(id):
        action = Action.query.filter_by(id=id).first()

        if action:
            parl_id = action.parlementaire_id

            if action.attachment:
                path = os.path.join(uploads_root, action.attachment)
                if os.path.exists(path):
                    os.unlink(path)

            db.session.delete(action)
            db.session.flush()

            last_action = (
                Action.query.filter(Action.parlementaire_id == parl_id)
                .order_by(Action.etape.desc())
                .first()
            )

            if last_action and last_action.etape > ETAPE_A_ENVOYER:
                etape = last_action.etape
            else:
                etape = ETAPE_A_ENVOYER

            parl = Parlementaire.query.filter_by(id=parl_id).first()
            parl.etape = etape

            db.session.commit()

        return redirect_back()

    @app.route("/admin/publish/<id>", endpoint="admin_publish")
    @require_admin
    def admin_publish(id):
        action = (
            Action.query.filter(
                Action.etape.in_(
                    [ETAPE_COM_A_MODERER, ETAPE_DOC_MASQUE, ETAPE_DOC_PUBLIE]
                )
            )
            .filter(Action.id == id)
            .first()
        )

        if action:
            if action.etape == ETAPE_COM_A_MODERER:
                action.etape = ETAPE_COM_PUBLIE
            elif action.etape == ETAPE_DOC_PUBLIE:
                action.etape = ETAPE_DOC_MASQUE
            elif action.etape == ETAPE_DOC_MASQUE:
                action.etape = ETAPE_DOC_PUBLIE

            db.session.commit()

        return redirect_back()

    @app.route("/admin/fichier/<id_action>", endpoint="admin_fichier")
    @require_admin
    def admin_fichier(id_action):
        act = Action.query.filter_by(id=id_action).first()

        if not act or not act.attachment:
            return not_found()

        path = os.path.join(app.config["DATA_DIR"], act.attachment)
        ext = path.rsplit(".", 1)[1].lower()

        with open(path, "rb") as fichier:
            response = make_response(fichier.read())
            response.headers["Content-Type"] = EXTENSIONS[ext]
            return response

    @app.route("/admin/action/<id_parl>", endpoint="admin_action", methods=["POST"])
    @require_admin
    def admin_action(id_parl):
        parl = Parlementaire.query.filter_by(id=id_parl).first()
        if not parl:
            return not_found()

        try:
            etape = int(request.form["etape"])
        except ValueError:
            etape = None

        if etape is None or etape not in ETAPES_BY_ORDRE:
            msg = "Étape inconnue."
            return redirect_back(
                error=msg, fallback=url_for("parlementaire", id=id_parl)
            )

        if etape in (ETAPE_DOC_MASQUE, ETAPE_DOC_PUBLIE):
            prefix = "document"
        else:
            prefix = "etape-%s" % etape

        try:
            filename = handle_upload(
                uploads_root, "%s-%s" % (prefix, slugify(parl.nom_complet))
            )
        except Exception as e:
            return redirect_back(
                error=str(e), fallback=url_for("parlementaire", id=id_parl)
            )

        etape_data = ETAPES_BY_ORDRE[etape]

        if etape > 0:
            parl.etape = etape

        action = Action(
            date=datetime.now(),
            user=User.query.filter(User.id == session["user"]["id"]).one(),
            ip=remote_addr(),
            parlementaire=parl,
            etape=etape,
            attachment=filename,
            suivi=request.form["suivi"],
        )

        db.session.add(action)
        db.session.commit()

        if etape_data["alerte"]:
            cnt = envoyer_alerte(app, etape_data, parl, request.form["suivi"])
            if cnt:
                flash("%s e-mails d'alerte envoyés" % cnt, category="success")

        return redirect(url_for("parlementaire", id=id_parl))
