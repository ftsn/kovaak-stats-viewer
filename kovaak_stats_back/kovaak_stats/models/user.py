from kovaak_stats.app import db
from kovaak_stats.utils.users import hash_pw
from base64 import b64decode
from bcrypt import checkpw
import binascii
import datetime


class AuthenticationError(Exception):
    """Exception class for every authentication error"""
    pass


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    creation_date = db.Column(db.DateTime(), default=datetime.datetime.now)
    modification_date = db.Column(db.DateTime(), default=datetime.datetime.now, onupdate=datetime.datetime.now)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email_addr = db.Column(db.String(80), unique=True, nullable=False)
    hashed_pw = db.Column(db.String(80), nullable=False)

    # Flask-login
    _authenticated = False
    _active = False
    _anonymous = False

    def __repr__(self):
        return 'My id is {} and my name is {}'.format(self.id, self.name)

    @classmethod
    def create(cls, username, email_addr, clear_pw):
        user = cls(name=username,
                   email_addr=email_addr,
                   hashed_pw=hash_pw(clear_pw).decode('utf-8'))
        db.session.add(user)
        return user

    @classmethod
    def from_db(cls, username):
        return User.query.filter_by(name=username).first()

    @classmethod
    def from_basic_auth(cls, token):
        try:
            decoded = b64decode(token).decode('utf-8').split(':')
        except (binascii.Error, UnicodeDecodeError):
            raise AuthenticationError
        username = decoded[0]
        password = ':'.join(decoded[1:]).encode('utf-8')
        user = cls.from_db(username)
        if not user:
            return None
        if checkpw(password, user.hashed_pw.encode('utf-8')):
            return User
        return None

    @property
    def is_authenticated(self):
        """needed for Flask-Login"""
        return self._authenticated

    @is_authenticated.setter
    def is_authenticated(self, value):
        """needed for Flask-Login"""
        self._authenticated = value

    @property
    def is_active(self):
        """needed for Flask-Login"""
        return self._active

    @is_active.setter
    def is_active(self, value):
        """needed for Flask-Login"""
        self._active = value

    @property
    def is_anonymous(self):
        """needed for Flask-Login"""
        return self._anonymous

    @is_anonymous.setter
    def is_anonymous(self, value):
        """needed for Flask-Login"""
        self._anonymous = value

    def get_id(self):
        """needed for Flask-Login"""
        return self.name
