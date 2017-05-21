# -*- coding: utf-8 -*-

from .database import db


class Action(db.Model):
    __tablename__ = 'actions'

    id = db.Column(db.Integer, primary_key=True)

    date = db.Column(db.DateTime)
    ip = db.Column(db.Unicode)

    suivi = db.Column(db.Unicode)
    attachment = db.Column(db.Unicode)

    etape = db.Column(db.Integer)

    parlementaire_id = db.Column(db.Integer,
                                 db.ForeignKey('parlementaires.id'))
    parlementaire = db.relationship('Parlementaire', back_populates='actions')

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='actions')
