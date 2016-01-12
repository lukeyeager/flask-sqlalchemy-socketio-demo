from __future__ import absolute_import

import json

import socketIO_client

from myapp import config
from myapp.webserver.webapp import webapp
from myapp.webserver.socketio import socketio as socketio_server


@socketio_server.on('worker update', namespace='/worker')
def worker_request(data):
    print 'SocketIO worker update -', data
    print 'Sending to SocketIO ...'
    socketio_server.emit(
        'new_update',
        data['msg'] + ' at ' + data['timestamp'],
        namespace='/browser',
    )


class WorkerNamespace(socketIO_client.BaseNamespace):
    pass


def send_update(update):
    data = {'msg': update.msg, 'timestamp': str(update.timestamp)}

    with socketIO_client.SocketIO('localhost', 5000) as socketio_client:
        print 'Sending SocketIO update to server ...'
#        namespace = socketio_client.define(socketIO_client.BaseNamespace, '/worker')
#        namespace.emit('worker update', data)
        socketio_client.emit('worker update', data, path='/worker')
