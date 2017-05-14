# -*- coding: utf-8 -*-

from datetime import date
import os

from flask import render_template, request
from xhtml2pdf import pisa

from .text import slugify


EXTENSIONS = {
    'pdf': 'application/pdf',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
}


def generer_demande(parl, directory, force=False):
    filename = 'demande-irfm-%s.pdf' % slugify(parl.nom_complet)
    path = os.path.join(directory, filename)

    aujourdhui = date.today()
    m = aujourdhui.month - 6
    y = aujourdhui.year
    if m < 1:
        m = m + 12
        y = y - 1

    debut = max(date(y, m, aujourdhui.day),
                date(parl.mandat_debut.year, parl.mandat_debut.month, 1))

    generer_pdf('courriers/demande.html.j2', {
                    'parlementaire': parl,
                    'aujourdhui': aujourdhui.strftime('%d %B %Y'),
                    'debut_releves': debut.strftime('%B %Y'),
                    'fin_releves': aujourdhui.strftime('%B %Y'),
                    'declaration': debut < date(2017, 1, 1)
                },
                path,
                force)

    return filename


def generer_pdf(template, data, path, force=False):
    if force or not os.path.exists(path):
        html = render_template(template, **data)

        with open(path, 'wb') as pdf:
            pisa.CreatePDF(html, pdf)


def handle_upload(directory, basename, key='file'):
    filename = None

    if request.files.get(key) and request.files[key].filename != '':
        file = request.files[key]
        ext = file.filename.rsplit('.', 1)[1].lower()

        if ext not in EXTENSIONS.keys():
            msg = 'Type de fichier non pris en charge, merci d\'envoyer ' \
                  'uniquement un fichier PDF, JPG ou PNG'
            raise Exception(msg)

        if ext == 'jpeg':
            ext = 'jpg'

        filename = '%s.%s' % (basename, ext)
        file.save(os.path.join(directory, filename))

    return filename


