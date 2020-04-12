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
    def create(cls, token_type, username=None):
        if token_type not in ['access', 'refresh']:
            return None
        token = cls()
        if token_type == 'refresh':
            token.value = secrets.token_urlsafe(40)
            exp = datetime.datetime.now() + datetime.timedelta(days=current_app.config.get('REFRESH_TOKEN_DURATION'))
            token.expiration_date = exp
            token.type = 'REFRESH'
        else:
            from kovaak_stats.models.user import User
            user = User.from_db(username)
            rightlist = list(map(lambda x: x.name, user.rights))
            payload = {
                'sub': username,
                'rights': rightlist,
                'iat': datetime.datetime.now(),
                'exp': datetime.datetime.now() + datetime.timedelta(minutes=int(current_app.config.get('JWT_DURATION')))
            }
            token.value = jwt.encode(payload, current_app.config.get('JWT_SECRET')).decode('unicode_escape')
            exp = datetime.datetime.now() + datetime.timedelta(minutes=current_app.config.get('JWT_DURATION'))
            token.expiration_date = exp
            token.type = 'JWT'
        db.session.add(token)
        return token

    @classmethod
    def from_db(cls, value):
        return cls.query.filter_by(value=value).first()

    def delete(self):
        db.session.delete(self)

    @classmethod
    def create_pair(cls, user):
        if user.tokens:
            user.tokens[0].delete()
            user.tokens[1].delete()
            db.session.commit()
        access_token = cls.create('access', user.name)
        refresh_token = cls.create('refresh')
        access_token.linked_token = refresh_token.value
        refresh_token.linked_token = access_token.value
        user.tokens.append(access_token)
        user.tokens.append(refresh_token)
        return access_token, refresh_token

    @classmethod
    def renew_refresh_token(cls, access_token):
        refresh_token = cls.create('refresh')
        refresh_token.linked_token = access_token.value
        access_token.linked_token = refresh_token.value
        access_token.user.tokens.append(refresh_token)
        return refresh_token

    def is_linked(self, token_value):
        return self.linked_token == token_value

    def refresh(self):
        exp = datetime.datetime.now() + datetime.timedelta(minutes=int(current_app.config.get('JWT_DURATION')))
        self.expiration_date = exp

    def has_expired(self):
        return self.expiration_date < datetime.datetime.now()
