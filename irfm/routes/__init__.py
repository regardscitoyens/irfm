# -*- coding: utf-8 -*-

from .context_processors import setup as setup_cp
from .filters import setup as setup_filters

from .home import setup_routes as setup_home
from .parlementaires import setup_routes as setup_parl


def setup_routes(app):
    setup_cp(app)
    setup_filters(app)
    setup_home(app)
    setup_parl(app)
