from __future__ import absolute_import

import json

import redis

from myapp import config
from myapp.webserver.webapp import webapp
from myapp.webserver.socketio import socketio

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
                socketio.emit('new_update', data['msg'] + ' at ' + data['timestamp'])

@webapp.before_first_request
def start_listener():
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

    thread = create_thread_func(listen_thread)
    start_thread_func(thread)

def shutdown_listener():
    redis.StrictRedis().publish(config.REDIS_CHANNEL, 'KILL')

def send_update(update):
    redis.StrictRedis().publish(
        config.REDIS_CHANNEL,
        json.dumps({'msg': update.msg, 'timestamp': str(update.timestamp)}))
    print 'REDIS - published ', update
