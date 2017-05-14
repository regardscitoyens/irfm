# -*- coding: utf-8 -*-

from flask import request


EXTENSIONS = {
    'pdf': 'application/pdf',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
}


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
