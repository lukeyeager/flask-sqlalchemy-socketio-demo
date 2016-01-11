import flask

from myapp.database.models import Update
from myapp.database.adapter import db

blueprint = flask.Blueprint(__name__, __name__)

@blueprint.route('/')
def index():
    updates = Update.query.all()
    return flask.render_template('index.html', updates=updates)

@blueprint.route('/delete')
def delete():
    Update.query.delete()
    db.session.commit()
    return flask.redirect(flask.url_for('.index'))
