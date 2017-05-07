# -*- coding: utf-8 -*-

from .context_processors import setup as setup_cp
from .filters import setup as setup_filters

from .admin import setup_routes as setup_admin
from .home import setup_routes as setup_home
from .parlementaires import setup_routes as setup_parl
from .pdf import setup_routes as setup_pdf
from .session import setup_routes as setup_session


def setup_routes(app):
    setup_cp(app)
    setup_filters(app)
    setup_home(app)
    setup_session(app)
    setup_parl(app)
    setup_pdf(app)
    setup_admin(app)
