from __future__ import absolute_import

import socketIO_client

from myapp.webserver.socketio import socketio as socketio_server


@socketio_server.on('worker update', namespace='/worker')
def worker_request(data):
    print('SocketIO worker update -', data)
    socketio_server.emit(
        'new_update',
        data['msg'] + ' at ' + data['timestamp'],
        namespace='/browser',
    )


def send_update(update):
    data = {'msg': update.msg, 'timestamp': str(update.timestamp)}

    with socketIO_client.SocketIO('localhost', 5000) as socketio_client:
        socketio_client.emit('worker update', data, path='/worker')
        print('SocketIO - sent')
