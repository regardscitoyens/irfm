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
