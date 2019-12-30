from kovaak_stats.app import db
from kovaak_stats.utils.users import hash_pw


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email_addr = db.Column(db.String(80), unique=True, nullable=False)
    hashed_pw = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return 'My id is {} and my name is {}'.format(self.id, self.username)

    @classmethod
    def create(cls, username, email_addr, clear_pw):
        user = cls(username=username,
                   email_addr=email_addr,
                   hashed_pw=hash_pw(clear_pw).decode('utf-8'))
        db.session.add(user)
        return user

    def from_db(self, username):
        self.query.filter_by(username=username).first()
