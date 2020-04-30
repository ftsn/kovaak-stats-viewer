from kovaak_stats.app import db
from kovaak_stats.utils.users import code_gen
from flask import current_app
import datetime


class RecoveryCode(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    creation_date = db.Column(db.DateTime(), default=datetime.datetime.now)
    modification_date = db.Column(db.DateTime(), default=datetime.datetime.now, onupdate=datetime.datetime.now)
    expiration_date = db.Column(db.DateTime())
    value = db.Column(db.String(8), unique=True, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    @classmethod
    def create(cls):
        recovery_code = cls()
        recovery_code.value = code_gen()
        exp = datetime.datetime.now() + datetime.timedelta(minutes=current_app.config.get('RECOVERY_CODE_DURATION'))
        recovery_code.expiration_date = exp
        db.session.add(recovery_code)
        return recovery_code

    def delete(self):
        db.session.delete(self)

    @classmethod
    def from_db(cls, value, user_id):
        return cls.query.filter_by(value=value, user_id=user_id).first()

    def has_expired(self):
        if self.expiration_date < datetime.datetime.now():
            return True
        return False
