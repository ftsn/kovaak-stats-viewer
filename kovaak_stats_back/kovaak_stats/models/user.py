from kovaak_stats.app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return 'My id is {} and my name is {}'.format(self.id, self.username)

    @classmethod
    def create(cls, username=None):
        user = cls(username=username)
        print('Gonna save' + username)
        db.session.add(user)
        return user
