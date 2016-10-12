# flask-sqlalchemy-socketio-demo

[![Build Status](https://travis-ci.org/lukeyeager/flask-sqlalchemy-socketio-demo.svg?branch=master)](https://travis-ci.org/lukeyeager/flask-sqlalchemy-socketio-demo)

Demo for how to use Flask, SQLAlchemy and SocketIO together

### Setup
```
pip install -r requirements.txt
./manage.py db init
./manage.py db migrate
./manage.py db upgrade
```

#### Asynchronous framework
There are three options for the asynchronous backend framework:

1. eventlet
  * `pip install eventlet`
2. gevent
  * `pip install gevent gevent-websocket`
3. threading
  * *built-in*

#### Communication method
There are three options for the worker-server communication method:

1. SocketIO
  * `pip install socketio-client`
2. Redis
  * `pip install redis`
3. ZeroMQ
  * `pip install pyzmq`

### Run server
```
./manage.py runserver
```

### Test functionality
```
./manage.py add
```
