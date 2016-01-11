#!/usr/bin/env python2
"""
Demo in a single file
"""

import datetime
import threading

import flask
from flask.ext import migrate as flask_migrate
from flask.ext import script as flask_script
from flask.ext import sqlalchemy as sa
import flask_socketio
import redis


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
        print 'SQLALCHEMY - %s %s' % (change, obj)


### Flask-Migrate

flask_migrate.Migrate(app, db)
manager.add_command('db', flask_migrate.MigrateCommand)


### SocketIO

socketio = flask_socketio.SocketIO(app)

@socketio.on('connect')
def on_connect():
    print 'SocketIO connected.'

@socketio.on('disconnect')
def on_disconnect():
    print 'SocketIO disconnected.'


### Redis

class RedisListener(threading.Thread):
    def __init__(self, channels):
        threading.Thread.__init__(self)
        self.redis = redis.StrictRedis()
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe(channels)

    def work(self, item):
        print 'REDIS -', item['channel'], ":", item['data']
        with app.app_context():
            print 'Sending to SocketIO ...'
            socketio.emit('new_update', item['data'])

    def run(self):
        for item in self.pubsub.listen():
            if item['data'] == "KILL":
                self.pubsub.unsubscribe()
                print self, "unsubscribed and finished"
                break
            elif item['data'] != 1:
                self.work(item)


### Commands

@manager.command
def run_socketio():
    client = RedisListener(['new_update'])
    client.start()

    try:
        socketio.run(app, host='0.0.0.0')
    except KeyboardInterrupt:
        redis.StrictRedis().publish('new_update', 'KILL')

@manager.command
def add():
    u = Update(msg='Added from command-line')
    with app.app_context():
        print 'Committing to database ...'
        db.session.add(u)
        db.session.commit()
        print 'Publishing to redis ...'
        r = redis.StrictRedis()
        r.publish('new_update', {'msg': u.msg, 'timestamp': str(u.timestamp)})
        print 'Added', u

@manager.command
def delete():
    with app.app_context():
        Update.query.delete()
        db.session.commit()
        print 'Deleted all updates'


if __name__ == '__main__':
    manager.run()
