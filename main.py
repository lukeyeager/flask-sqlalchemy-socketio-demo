#!/usr/bin/env python2
"""
Manager for single-file application
"""

import datetime
import json

import flask
from flask.ext import migrate as flask_migrate
from flask.ext import script as flask_script
from flask.ext import sqlalchemy as sa
import flask_socketio
import redis


# Flask application

app = flask.Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


@app.route('/')
def index():
    updates = Update.query.all()
    return flask.render_template('index.html', updates=updates)


@app.route('/delete')
def delete_route():
    delete_all_updates()
    return flask.redirect(flask.url_for('index'))


def delete_all_updates():
    """Can be invoked via HTTP or command-line"""
    Update.query.delete()
    db.session.commit()
    print 'Deleted all updates'

# Flask-Script

manager = flask_script.Manager(app)


# Flask-SQLAlchemy

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


# Flask-Migrate

flask_migrate.Migrate(app, db)
manager.add_command('db', flask_migrate.MigrateCommand)


# SocketIO

socketio = flask_socketio.SocketIO(app)


@socketio.on('connect')
def on_connect():
    print 'SocketIO connected.'


@socketio.on('disconnect')
def on_disconnect():
    print 'SocketIO disconnected.'


# Redis

def listen_redis():
    r = redis.StrictRedis()
    pubsub = r.pubsub()
    pubsub.subscribe(['new_update'])
    for item in pubsub.listen():
        if item['data'] == "KILL":
            pubsub.unsubscribe()
            print 'REDIS - unsubscribed and finished'
            break
        elif item['data'] != 1:
            print 'REDIS -', item['channel'], ":", item['data']
            with app.app_context():
                data = json.loads(item['data'])
                print 'Sending to SocketIO ...'
                socketio.emit('new_update', data['msg'] + ' at ' + data['timestamp'])


# Commands

@manager.command
def runserver(debug=False, use_reloader=False):
    create_thread_func = None
    start_thread_func = None
    try:
        import eventlet
        eventlet.monkey_patch()
        print 'Using eventlet'
        create_thread_func = lambda f: f
        start_thread_func = lambda f: eventlet.spawn(f)
    except ImportError:
        try:
            import gevent
            import gevent.monkey
            gevent.monkey.patch_all()
            print 'Using gevent'
            create_thread_func = lambda f: gevent.Greenlet(f)
            start_thread_func = lambda t: t.start()
        except ImportError:
            import threading
            print 'Using threading'
            create_thread_func = lambda f: threading.Thread(target=f)
            start_thread_func = lambda t: t.start()

    thread = create_thread_func(listen_redis)
    start_thread_func(thread)

    try:
        socketio.run(app, host='0.0.0.0', debug=debug, use_reloader=use_reloader)
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
        r.publish('new_update', json.dumps({'msg': u.msg, 'timestamp': str(u.timestamp)}))
        print 'Added', u


@manager.command
def delete():
    with app.app_context():
        delete_all_updates()


if __name__ == '__main__':
    manager.run()
