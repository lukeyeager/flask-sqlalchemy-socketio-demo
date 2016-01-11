#!/usr/bin/env python2

from flask.ext import migrate as flask_migrate
from flask.ext import script as flask_script

from myapp.database import models
from myapp.database.adapter import db
from myapp.database.models import Update
from myapp.webserver import redis as myapp_redis
from myapp.webserver.socketio import socketio
from myapp.webserver.webapp import webapp


manager = flask_script.Manager(webapp)
flask_migrate.Migrate(webapp, db)
manager.add_command('db', flask_migrate.MigrateCommand)


@manager.command
def runserver(debug=False, use_reloader=False):
    socketio.run(webapp, host='0.0.0.0', debug=debug, use_reloader=use_reloader)


@manager.command
def add():
    u = Update(msg='Added from command-line')
    with webapp.app_context():
        print 'Committing to database ...'
        db.session.add(u)
        db.session.commit()
        myapp_redis.send_update(u)


@manager.command
def delete():
    with webapp.app_context():
        models.Update.query.delete()
        db.session.commit()
    print 'Deleted all updates.'


if __name__ == '__main__':
    manager.run()
