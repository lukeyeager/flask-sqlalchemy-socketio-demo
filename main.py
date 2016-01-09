#!/usr/bin/env python2
"""
Demo in a single file
"""

import datetime

import flask
from flask.ext import migrate as flask_migrate
from flask.ext import script as flask_script
from flask.ext import sqlalchemy as sa
import flask_socketio

### Flask application

app = flask.Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

@app.route('/')
def index():
    updates = Update.query.all()
    return flask.render_template('index.html', updates=updates)

### Flask-Script

manager = flask_script.Manager(app)

### Flask-SQLAlchemy

db = sa.SQLAlchemy(app)

class Update(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    msg = db.Column(db.String(128))
    def __repr__(self):
        return r'<Update "%s" at %s>' % (self.msg, self.timestamp)

@sa.models_committed.connect_via(app)
def on_models_committed(sender, changes):
    for obj, change in changes:
        print 'PUBLISH - %s %s' % (change, obj)

### Flask-Migrate

flask_migrate.Migrate(app, db)
manager.add_command('db', flask_migrate.MigrateCommand)

@manager.command
def add_update():
    u = Update(msg='Added from command-line')
    with app.app_context():
        db.session.add(u)
        db.session.commit()
        print 'Added', u

### SocketIO

socketio = flask_socketio.SocketIO(app)

@manager.command
def run_socketio():
    socketio.run(app, host='0.0.0.0')


if __name__ == '__main__':
    manager.run()
