# -*- coding: utf-8 -*-

import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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
    API_PAGE_SIZE = 10
    SECRET_KEY = 'no-secret-key'
    PIWIK_HOST = None
    PIWIK_ID = None


class DebugConfig(DefaultConfig):
    """
    Debug-enabled default config
    """
    DEBUG = True
    SQLALCHEMY_ECHO = True


class AutoSecretKeyConfig(DefaultConfig):
    """
    Default config that automatically generates a secret key in DATA_DIR
    """
    _secret_key = None

    @property
    def SECRET_KEY(self):
        if not self._secret_key:
            secret_file = os.path.join(self.DATA_DIR, 'secret.txt')

            if not os.path.exists(secret_file):
                chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'

                from random import SystemRandom
                rnd = SystemRandom()
                key = ''.join([chars[rnd.randint(1, len(chars))-1]
                               for i in range(1, 50)])

                with open(secret_file, 'w+') as f:
                    f.write(key)

            with open(secret_file, 'r') as f:
                self._secret_key = f.read()

        return self._secret_key


class EnvironmentConfig(AutoSecretKeyConfig):
    """
    Config for environment-based setup.
    - IRFM_DEBUG: 'True' to enable
    - IRFM_DEBUG_SQL: 'True' to enable
    - IRFM_DB_URL: database connection URL
    - IRFM_DATA_DIR: directory for data files
    - IRFM_PIWIK_HOST: piwik hostname
    - IRFM_PIWIK_ID: piwik site ID
    """
    DEBUG = os.environ.get('IRFM_DEBUG', 'False') == 'True'
    SQLALCHEMY_ECHO = os.environ.get('IRFM_DEBUG_SQL', 'False') == 'True'

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'IRFM_DB_URL', DefaultConfig.SQLALCHEMY_DATABASE_URI)

    DATA_DIR = os.environ.get('IRFM_DATA_DIR', DefaultConfig.DATA_DIR)

    PIWIK_HOST = os.environ.get('IRFM_PIWIK_HOST', DefaultConfig.PIWIK_HOST)
    PIWIK_ID = os.environ.get('IRFM_PIWIK_ID', DefaultConfig.PIWIK_ID)
