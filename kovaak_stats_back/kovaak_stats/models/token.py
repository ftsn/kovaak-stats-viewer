from kovaak_stats.app import db
from flask import current_app
import datetime
import secrets
import jwt


class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    creation_date = db.Column(db.DateTime(), default=datetime.datetime.now)
    modification_date = db.Column(db.DateTime(), default=datetime.datetime.now, onupdate=datetime.datetime.now)
    expiration_date = db.Column(db.DateTime())
    value = db.Column(db.String, unique=True, nullable=False)
    type = db.Column(db.String(80), nullable=False)
    linked_token = db.Column(db.String, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    @classmethod
    def create(cls, token_type, user=None):
        if token_type not in ['access', 'refresh']:
            return None
        token = cls()
        if token_type == 'refresh':
            token.value = secrets.token_urlsafe(40)
            token.expiration_date = (datetime.datetime.now() +
                                     datetime.timedelta(days=current_app.config.get('REFRESH_TOKEN_DURATION')))
            token.type = 'REFRESH'
        else:
            payload = {
                'sub': user.name,
                'iat': datetime.datetime.now(),
                'exp': datetime.datetime.now() + datetime.timedelta(minutes=int(current_app.config.get('JWT_DURATION')))
            }
            token.value = jwt.encode(payload, current_app.config.get('JWT_SECRET')).decode('unicode_escape')
            token.expiration_date = (datetime.datetime.now() +
                                     datetime.timedelta(minutes=current_app.config.get('JWT_DURATION')))
            token.type = 'JWT'
        db.session.add(token)
        return token

    @classmethod
    def from_db(cls, value):
        return cls.query.filter_by(value=value).first()

    def delete(self):
        db.session.delete(self)

    def is_linked(self, token_value):
        return self.linked_token == token_value

    def refresh(self):
        self.expiration_date = (datetime.datetime.now() +
                                datetime.timedelta(minutes=int(current_app.config.get('JWT_DURATION'))))

    def has_expired(self):
        return self.expiration_date < datetime.datetime.now()
