from kovaak_stats.app import db
import datetime
import secrets


class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    creation_date = db.Column(db.DateTime(), default=datetime.datetime.now)
    modification_date = db.Column(db.DateTime(), default=datetime.datetime.now, onupdate=datetime.datetime.now)
    expiration_date = db.Column(db.DateTime())
    value = db.Column(db.String(80), unique=True, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    @classmethod
    def create(cls, token_type):
        if token_type not in ['access', 'refresh']:
            return None
        token = cls()
        if token_type == 'refresh':
            token.value = secrets.token_urlsafe(20)

    @classmethod
    def from_db(cls, value):
        return cls.query.filter_by(value=value).first()
