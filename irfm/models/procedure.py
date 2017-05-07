# -*- coding: utf-8 -*-

from .constants import ETAPES
from .database import db


class Etape(db.Model):
    __tablename__ = 'etapes'

    id = db.Column(db.Integer, primary_key=True)

    ordre = db.Column(db.Integer)
    label = db.Column(db.Unicode)
    description = db.Column(db.Unicode)
    couleur = db.Column(db.Unicode)

    parlementaires = db.relationship('Parlementaire', back_populates='etape')


class Action(db.Model):
    __tablename__ = 'actions'

    id = db.Column(db.Integer, primary_key=True)

    date = db.Column(db.DateTime)
    nick = db.Column(db.Unicode)
    email = db.Column(db.Unicode)
    attachment = db.Column(db.Unicode)

    etape_id = db.Column(db.Integer, db.ForeignKey('etapes.id'))
    etape = db.relationship('Etape')

    parlementaire_id = db.Column(db.Integer, db.ForeignKey('parlementaires.id'))
    parlementaire = db.relationship('Parlementaire', back_populates='actions')
