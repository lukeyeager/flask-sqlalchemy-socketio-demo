from __future__ import absolute_import

import flask

from myapp.database.models import Update
from myapp.database.adapter import db

blueprint = flask.Blueprint(__name__, __name__)


@blueprint.route('/')
@blueprint.route('/index')
def index():
    updates = Update.query.all()
    return flask.render_template('index.html', updates=updates)


@blueprint.route('/index.json')
def index_json():
    updates = Update.query.all()
    return flask.jsonify({'updates': [str(u) for u in updates]})


@blueprint.route('/delete', methods=['GET', 'POST'])
def delete():
    Update.query.delete()
    db.session.commit()
    return flask.redirect(flask.url_for('.index'))
