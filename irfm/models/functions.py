# -*- coding: utf-8 -*-

from sqlalchemy.sql.functions import ReturnTypeFromArgs


class unaccent(ReturnTypeFromArgs):
    pass


class replace(ReturnTypeFromArgs):
    pass


def normalize_name(field):
    return unaccent(replace(field, '-', ' '))
