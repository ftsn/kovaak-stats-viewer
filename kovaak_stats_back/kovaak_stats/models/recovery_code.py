from kovaak_stats.app import db
from kovaak_stats.utils.users import code_gen
import datetime


class RecoveryCode(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    creation_date = db.Column(db.DateTime(), default=datetime.datetime.now)
    modification_date = db.Column(db.DateTime(), default=datetime.datetime.now, onupdate=datetime.datetime.now)
    value = db.Column(db.String(8), unique=True, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    @classmethod
    def create(cls):
        recovery_code = cls()
        recovery_code.value = code_gen()
        db.session.add(recovery_code)
        return recovery_code

    @classmethod
    def from_db(cls, value, user_id):
        return cls.query.filter_by(value=value, user_id=user_id).first()

    def has_expired(self):
        expiration_time = self.creation_date + datetime.timedelta(minutes=1)
        if datetime.datetime.now() < expiration_time:
            return False
        return True
