from __future__ import absolute_import

import datetime

from .adapter import db


class Update(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    msg = db.Column(db.String(128))

    def __repr__(self):
        return r'<Update "%s" at %s>' % (self.msg, self.timestamp)
