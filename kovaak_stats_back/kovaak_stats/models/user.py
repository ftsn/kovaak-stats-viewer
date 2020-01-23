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
    hashed_pw = db.Column(db.String(80), nullable=False)

    # Flask-login
    _authenticated = False
    _active = False
    _anonymous = False

    def __repr__(self):
        return 'My id is {} and my name is {}'.format(self.id, self.name)

    @classmethod
    def create(cls, username, email_addr, clear_pw):
        if cls.exists(username):
            raise ValueError('The user {} already exists.'.format(username))
        if cls.email_addr_exists(email_addr):
            raise ValueError('The email address {} already exists.'.format(email_addr))
        user = cls(name=username,
                   email_addr=email_addr,
                   hashed_pw=hash_pw(clear_pw).decode('utf-8'))
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
        self.rights.append(right)

    def del_right_from_string(self, name):
        from kovaak_stats.models.right import Right
        right = Right.from_db(name)
        self.rights.remove(right)

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
