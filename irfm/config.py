# -*- coding: utf-8 -*-

import os
from random import SystemRandom


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_secret_key(data_dir):
    secret_file = os.path.join(data_dir, 'secret.txt')

    if not os.path.exists(secret_file):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'

        rnd = SystemRandom()
        key = ''.join([chars[rnd.randint(1, len(chars)) - 1]
                       for i in range(1, 50)])

        with open(secret_file, 'w+') as f:
            f.write(key)

    with open(secret_file, 'r') as f:
        return f.read()


class DefaultConfig(object):
    """
    Default irfm config file for standard environment
    """
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = \
        'postgresql://irfm:irfm@localhost:5432/irfm'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    MAX_CONTENT_LENGTH = 4 * 1024 * 1024
    PIWIK_HOST = None
    PIWIK_ID = None

    ADMIN_EMAIL = 'none@example.com'
    ADMIN_PASSWORD = None

    MAIL_SERVER = 'localhost'
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    MAIL_SUPPRESS_SEND = False

    PERMANENT_SESSION_LIFETIME = 6 * 31 * 24 * 60 * 60
    SERVER_NAME = 'irfm.regardscitoyens.org'


class DebugConfig(DefaultConfig):
    """
    Debug-enabled default config
    """
    DEBUG = True
    SQLALCHEMY_ECHO = True


class EnvironmentConfig(DefaultConfig):
    """
    Config for environment-based setup.
    - IRFM_DEBUG: 'True' to enable
    - IRFM_DEBUG_SQL: 'True' to enable
    - IRFM_DB_URL: database connection URL
    - IRFM_DATA_DIR: directory for data files
    - IRFM_PIWIK_HOST: piwik hostname
    - IRFM_PIWIK_ID: piwik site ID
    - IRFM_ADMIN_EMAIL: admin email
    - IRFM_ADMIN_PASSWORD: admin password as hashed by `irfm password`
    - IRFM_MAIL_SERVER:
    - IRFM_MAIL_PORT:
    - IRFM_MAIL_USE_TLS: 'True' to enable
    - IRFM_MAIL_USE_SSL: 'True' to enable
    - IRFM_MAIL_USERNAME:
    - IRFM_MAIL_PASSWORD:
    """
    DEBUG = os.environ.get('IRFM_DEBUG', 'False') == 'True'
    SQLALCHEMY_ECHO = os.environ.get('IRFM_DEBUG_SQL', 'False') == 'True'

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'IRFM_DB_URL', DefaultConfig.SQLALCHEMY_DATABASE_URI)

    DATA_DIR = os.environ.get('IRFM_DATA_DIR', DefaultConfig.DATA_DIR)

    PIWIK_HOST = os.environ.get('IRFM_PIWIK_HOST', DefaultConfig.PIWIK_HOST)
    PIWIK_ID = os.environ.get('IRFM_PIWIK_ID', DefaultConfig.PIWIK_ID)

    ADMIN_EMAIL = os.environ.get('IRFM_ADMIN_EMAIL', DefaultConfig.ADMIN_EMAIL)
    ADMIN_PASSWORD = os.environ.get('IRFM_ADMIN_PASSWORD',
                                    DefaultConfig.ADMIN_PASSWORD)

    MAIL_SERVER = os.environ.get('IRFM_MAIL_SERVER', DefaultConfig.MAIL_SERVER)
    MAIL_PORT = os.environ.get('IRFM_MAIL_PORT', DefaultConfig.MAIL_PORT)
    MAIL_USE_TLS = os.environ.get('IRFM_MAIL_USE_TLS', 'False') == 'True'
    MAIL_USE_SSL = os.environ.get('IRFM_MAIL_USE_SSL', 'False') == 'True'
    MAIL_USERNAME = os.environ.get('IRFM_MAIL_USERNAME',
                                   DefaultConfig.MAIL_USERNAME)
    MAIL_PASSWORD = os.environ.get('IRFM_MAIL_PASSWORD',
                                   DefaultConfig.MAIL_PASSWORD)

    MAIL_SUPPRESS_SEND = os.environ.get('IRFM_MAIL_SUPPRESS_SEND', 'False') \
        == 'True'
