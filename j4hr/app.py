# -*- coding: utf-8 -*-
import os
import logging
from logging import Formatter
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask.ext.assets import Environment
from flask.ext.login import LoginManager
from flask.ext.pymongo import PyMongo
from flask_oauthlib.client import OAuth
from flask_wtf.csrf import CsrfProtect
import redis
import requests
from rq import Queue
import sqlalchemy
from webassets.loaders import PythonLoader
from j4hr import assets
from j4hr.utils import ReverseProxied

app = Flask(__name__)

app.wsgi_app = ReverseProxied(app.wsgi_app)

# The environment variable, either 'prod' or 'dev'
env = os.environ.get('J4HR2_ENV', 'dev')

# Use the appropriate environment-specific settings
app.config.from_object(
    'j4hr.settings.{env}Config'.format(env=env.capitalize()))

app.config['ENV'] = env

# Set up logging
file_handler = RotatingFileHandler(app.config['LOG_FILE'])
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(Formatter(
    '%(asctime)s %(levelname)s: %(message)s '
    '[in %(pathname)s:%(lineno)d]'
))
app.logger.addHandler(file_handler)

if 'SENTRY_DSN' in app.config:
    from raven.contrib.flask import Sentry
    sentry = Sentry(app)

CsrfProtect(app)

mongo = PyMongo(app)

login_manager = LoginManager()
login_manager.init_app(app)

eve_db = sqlalchemy.create_engine(app.config['EVE_STATIC_DUMP'])

oauth = OAuth(app)
hr_oauth = oauth.remote_app(
    'j4hr2',
    app_key='J4OAUTH'
)

rQueue = Queue('hr2', connection=redis.StrictRedis(app.config['REDIS']))

api_oauth = requests.Session()
api_oauth.headers.update({
    'x-oauth-key': app.config['J4OAUTH']['consumer_key'],
    'x-oauth-secret': app.config['J4OAUTH']['consumer_secret']})


# Register asset bundles
assets_env = Environment()
assets_env.init_app(app)
assets_loader = PythonLoader(assets)
for name, bundle in assets_loader.load_bundles().iteritems():
    assets_env.register(name, bundle)
