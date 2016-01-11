from __future__ import absolute_import

import flask

from . import views
from myapp.database.adapter import db

webapp = flask.Flask(__name__)
webapp.config.from_object('myapp.config')

webapp.register_blueprint(views.blueprint)
db.init_app(webapp)
