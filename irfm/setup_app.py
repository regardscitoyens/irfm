# -*- coding: utf-8 -*-

import os

from flask import Flask
from flaskext.markdown import Markdown

from .routes import setup_routes


def setup_app(name):
    # Create app
    app = Flask(name)

    # Load config
    config_obj = os.environ.get('IRFM_CONFIG',
                                'irfm.config.DefaultConfig')
    app.config.from_object(config_obj)

    # Setup DB
    from .models import db
    db.init_app(app)

    # Enable Markdown
    Markdown(app)

    # Setup routes
    setup_routes(app)

    return app
