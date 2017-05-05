# -*- coding: utf-8 -*-

import enum

from .constants import CHAMBRES, ETAPES, SEXES
from .database import db



class Parlementaire(db.Model):
    __tablename__ = 'parlementaires'

    id = db.Column(db.Integer, primary_key=True)

    nom = db.Column(db.Unicode)
    prenom = db.Column(db.Unicode)
    sexe = db.Column(db.Enum(*SEXES.keys(), name='sexes'))
    adresse = db.Column(db.Unicode)

    chambre = db.Column(db.Enum(*CHAMBRES.keys(), name='chambres'))

    mandat_debut = db.Column(db.DateTime)
    mandat_fin = db.Column(db.DateTime)
    num_deptmt = db.Column(db.Integer)
    nom_circo = db.Column(db.Unicode)
    num_circo = db.Column(db.Integer)
    groupe = db.Column(db.Unicode)
    groupe_sigle = db.Column(db.Unicode)

    url_photo = db.Column(db.Unicode)
    url_rc = db.Column(db.Unicode)
    url_off = db.Column(db.Unicode)

    etat = db.Column(db.Enum(*ETAPES.keys(), name='etapes'))
