from __future__ import absolute_import

import os

import myapp

basedir = os.path.abspath(os.path.dirname(myapp.__file__))

# SQLAlchemy
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = True

# Redis
REDIS_CHANNEL = 'myapp:updates'

# ZeroMQ
ZEROMQ_PORT = 5556
