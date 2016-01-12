from __future__ import absolute_import

import json

import redis

from myapp import config
from myapp.webserver.webapp import webapp
from myapp.webserver.socketio import socketio

try:
    import eventlet
    print 'Using eventlet'
    eventlet.monkey_patch()
    spawn = eventlet.spawn
except ImportError:
    try:
        import gevent
        import gevent.monkey
        print 'Using gevent'
        gevent.monkey.patch_all()
        spawn = lambda f: gevent.Greenlet(f).start()
    except ImportError:
        import threading
        print 'Using threading'
        spawn = lambda f: threading.Thread(target=f).start()


def listen_thread():
    r = redis.StrictRedis()
    pubsub = r.pubsub()
    pubsub.subscribe([config.REDIS_CHANNEL])
    for item in pubsub.listen():
        if item['data'] == "KILL":
            pubsub.unsubscribe()
            print 'REDIS - unsubscribed and finished'
            break
        elif item['data'] != 1:
            print 'REDIS -', item['channel'], ":", item['data']
            with webapp.app_context():
                data = json.loads(item['data'])
                print 'Sending to SocketIO ...'
                socketio.emit(
                    'new_update',
                    data['msg'] + ' at ' + data['timestamp'],
                    namespace='/browser',
                )


@webapp.before_first_request
def start_listener():
    spawn(listen_thread)


def shutdown_listener():
    redis.StrictRedis().publish(config.REDIS_CHANNEL, 'KILL')


def send_update(update):
    data = {'msg': update.msg, 'timestamp': str(update.timestamp)}

    redis.StrictRedis().publish(
        config.REDIS_CHANNEL,
        json.dumps(data),
    )
    print 'REDIS - published ', update
