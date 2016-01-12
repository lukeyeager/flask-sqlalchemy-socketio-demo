from __future__ import absolute_import

import json

from myapp import config
from myapp.webserver.webapp import webapp
from myapp.webserver.socketio import socketio


try:
    import eventlet
    from eventlet.green import zmq
    print 'Using eventlet'
    eventlet.monkey_patch()
    spawn = eventlet.spawn
except ImportError:
    try:
        import gevent
        import gevent.monkey
        import zmq.green as zmq
        print 'Using gevent'
        gevent.monkey.patch_all()
        spawn = lambda f: gevent.Greenlet(f).start()
    except ImportError:
        import threading
        import zmq
        print 'Using threading'
        spawn = lambda f: threading.Thread(target=f).start()


def listen_thread():
    ctx = zmq.Context()
    # Reply - act as server
    socket = ctx.socket(zmq.REP)
    socket.bind('tcp://*:%s' % config.ZEROMQ_PORT)
    while True:
        print 'Listening to socket ...'
        request = socket.recv()
        print 'ZEROMQ request -', request
        socket.send('OK')

        if request == 'KILL':
            socket.close()
            print 'Socket closed.'
            break

        with webapp.app_context():
            data = json.loads(request)
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
    ctx = zmq.Context()
    # Request - act as client
    socket = ctx.socket(zmq.REQ)
    socket.connect('tcp://localhost:%s' % config.ZEROMQ_PORT)
    socket.send('KILL')
    _ = socket.recv() # ignore reply


def send_update(update):
    data = {'msg': update.msg, 'timestamp': str(update.timestamp)}

    ctx = zmq.Context()
    # Request - act as client
    socket = ctx.socket(zmq.REQ)
    socket.connect('tcp://localhost:%s' % config.ZEROMQ_PORT)
    socket.send(json.dumps(data))
    reply = socket.recv()
    print 'ZEROMQ reply -', reply
