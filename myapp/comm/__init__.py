from __future__ import absolute_import

try:
    import socketIO_client
    print 'Using socketio for comm'
    from .socketio import send_update
except ImportError:
    try:
        import redis
        print 'Using redis for comm'
        from .redis import send_update
    except ImportError:
        import zmq
        print 'Using zeromq for comm'
        from .zeromq import send_update
