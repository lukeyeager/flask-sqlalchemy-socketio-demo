import flask_socketio

from myapp.webserver.webapp import webapp

socketio = flask_socketio.SocketIO(webapp)

@socketio.on('connect')
def on_connect():
    print 'SocketIO connected.'

@socketio.on('disconnect')
def on_disconnect():
    print 'SocketIO disconnected.'
