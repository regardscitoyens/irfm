# -*- coding: utf-8 -*-

from .constants import CHAMBRES, SEXES
from .database import db


class Groupe(db.Model):
    __tablename__ = 'groupes'

    id = db.Column(db.Integer, primary_key=True)

    sigle = db.Column(db.Unicode)
    nom = db.Column(db.Unicode)
    chambre = db.Column(db.Enum(*CHAMBRES.keys(), name='chambres'))
    couleur = db.Column(db.Unicode)


class Parlementaire(db.Model):
    __tablename__ = 'parlementaires'

    id = db.Column(db.Integer, primary_key=True)

    nom = db.Column(db.Unicode)
    prenom = db.Column(db.Unicode)
    nom_complet = db.Column(db.Unicode)
    sexe = db.Column(db.Enum(*SEXES.keys(), name='sexes'))
    adresse = db.Column(db.Unicode)
    emails = db.Column(db.Unicode)
    twitter = db.Column(db.Unicode)

    chambre = db.Column(db.Enum(*CHAMBRES.keys(), name='chambres'))

    mandat_debut = db.Column(db.DateTime)
    mandat_fin = db.Column(db.DateTime)
    num_deptmt = db.Column(db.Unicode)
    nom_circo = db.Column(db.Unicode)
    num_circo = db.Column(db.Integer)

    groupe_id = db.Column(db.Integer, db.ForeignKey('groupes.id'))
    groupe = db.relationship('Groupe')

    url_photo = db.Column(db.Unicode)
    url_rc = db.Column(db.Unicode)
    url_off = db.Column(db.Unicode)

    etape_id = db.Column(db.Integer, db.ForeignKey('etapes.id'))
    etape = db.relationship('Etape', back_populates='parlementaires')

    actions = db.relationship('Action', back_populates='parlementaire',
                              order_by='Action.date')

    mails_envoyes = db.Column(db.Integer, default=0, server_default='0')
