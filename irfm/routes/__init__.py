# -*- coding: utf-8 -*-

from .abonnements import setup_routes as setup_abo
from .admin import setup_routes as setup_admin
from .context_processors import setup as setup_cp
from .files import setup_routes as setup_files
from .filters import setup as setup_filters
from .help import setup_routes as setup_help
from .home import setup_routes as setup_home
from .parlementaires import setup_routes as setup_parl
from .session import setup_routes as setup_session


def setup_routes(app):
    setup_cp(app)
    setup_filters(app)
    setup_home(app)
    setup_help(app)
    setup_session(app)
    setup_parl(app)
    setup_files(app)
    setup_admin(app)
    setup_abo(app)
