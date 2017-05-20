# -*- coding: utf-8 -*-

from .database import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    nick = db.Column(db.Unicode)
    email = db.Column(db.Unicode)

    admin = db.Column(db.Boolean)
    abo_rc = db.Column(db.Boolean)
    abo_membres = db.Column(db.Boolean)
    abo_irfm = db.Column(db.Boolean)

    actions = db.relationship('Action', back_populates='user',
                              order_by='Action.date')
