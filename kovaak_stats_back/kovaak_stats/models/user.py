from kovaak_stats.app import db
from kovaak_stats.utils.users import hash_pw
from base64 import b64decode
from bcrypt import checkpw
import binascii
import datetime
import jsonpatch


class AuthenticationError(Exception):
    """Exception class for every authentication error"""
    pass


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    creation_date = db.Column(db.DateTime(), default=datetime.datetime.now)
    modification_date = db.Column(db.DateTime(), default=datetime.datetime.now, onupdate=datetime.datetime.now)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email_addr = db.Column(db.String(80), unique=True, nullable=False)
    hashed_pw = db.Column(db.String(80))
    google_id = db.Column(db.Boolean)

    tokens = db.relationship('Token', backref='user', lazy='subquery', cascade="all, delete-orphan")
    recovery_code = db.relationship("RecoveryCode", uselist=False, backref="user")

    # Flask-login
    _authenticated = False
    _active = False
    _anonymous = False

    def __repr__(self):
        return self.name

    @classmethod
    def create(cls, username, email_addr, clear_pw):
        if cls.exists(username):
            raise ValueError('The user {} already exists.'.format(username))
        if cls.email_addr_exists(email_addr):
            raise ValueError('The email address {} already exists.'.format(email_addr))
        user = cls(name=username,
                   email_addr=email_addr,
                   hashed_pw=hash_pw(clear_pw).decode('utf-8'),
                   google_id=False)
        db.session.add(user)
        return user

    @classmethod
    def create_google(cls, email_addr):
        name = email_addr.split('@')[0]
        if cls.exists(name):
            raise ValueError('The user {} already exists.'.format(name))
        user = cls(name=name,
                   email_addr=email_addr,
                   hashed_pw=None,
                   google_id=True)
        db.session.add(user)
        return user

    def delete(self):
        db.session.delete(self)

    def modify(self, changes):
        obj = {
            "name": self.name,
            "email_addr": self.email_addr,
            "rights": self.rights_to_list()
        }
        patch = jsonpatch.JsonPatch.from_string(changes)
        patch.apply(obj, in_place=True)

        from kovaak_stats.models.right import Right
        for right in obj['rights']:
            if not Right.exists(right):
                raise ValueError('The right {} doesn\'t exist'.format(right))

        self.name = obj['name']
        self.email_addr = obj['email_addr']
        self.rights.clear()
        for right in obj['rights']:
            self.add_right_from_string(right)

    @classmethod
    def from_db(cls, username):
        return User.query.filter_by(name=username).first()

    @classmethod
    def from_db_basic(cls, username, password):
        user = User.query.filter_by(name=username).first()
        if not checkpw(password.encode('utf-8'), user.hashed_pw.encode('utf-8')):
            return None
        return user

    @classmethod
    def from_db_by_email(cls, email_addr):
        return User.query.filter_by(email_addr=email_addr).first()

    @classmethod
    def exists(cls, name):
        user = cls.query.filter_by(name=name).first()
        if user is None:
            return False
        return True

    @classmethod
    def email_addr_exists(cls, email_addr):
        user = cls.query.filter_by(email_addr=email_addr).first()
        if user is None:
            return False
        return True

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
            user.is_authenticated = True
            return user
        return None

    def has_right(self, name):
        for right in self.rights:
            if name == right.name:
                return True
        return False

    def rights_to_list(self):
        rights = []
        for right in self.rights:
            rights.append(right.name)
        return rights

    def add_right_from_string(self, name):
        from kovaak_stats.models.right import Right
        right = Right.from_db(name)
        if not right:
            raise ValueError('{} doesn\'t exist'.format(name))
        if right in self.rights:
            raise ValueError('{} already has the right {}'.format(self.name, name))
        self.rights.append(right)

    def del_right_from_string(self, name):
        from kovaak_stats.models.right import Right
        right = Right.from_db(name)
        if not right:
            raise ValueError('{} doesn\'t exist'.format(name))
        if right not in self.rights:
            raise ValueError('{} doesn\'t have the right {}'.format(self.name, name))
        self.rights.remove(right)

    def gen_recovery_code(self):
        from kovaak_stats.models.recovery_code import RecoveryCode
        if not self.recovery_code:
            recovery_code = RecoveryCode.create()
        else:
            if self.recovery_code.has_expired() is False:
                return None
            else:
                db.session.delete(self.recovery_code)
                recovery_code = RecoveryCode.create()
        self.recovery_code = recovery_code
        db.session.commit()
        return self.recovery_code.value

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
