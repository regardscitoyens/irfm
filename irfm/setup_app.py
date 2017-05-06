# -*- coding: utf-8 -*-

import os

from flask import Flask
from flaskext.markdown import Markdown

from .config import get_secret_key
from .routes import setup_routes



def setup_app(name):
    # Create app
    app = Flask(name)

    # Load config
    config_obj = os.environ.get('IRFM_CONFIG',
                                'irfm.config.DefaultConfig')
    app.config.from_object(config_obj)

    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = get_secret_key(app.config['DATA_DIR'])

    # Setup DB
    from .models import db
    db.init_app(app)

    # Enable Markdown
    Markdown(app)

    # Setup routes
    setup_routes(app)

    return app
