from kovaak_stats.app import db
import datetime

users_rights = db.Table(
    'users_rights',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('right_id', db.Integer, db.ForeignKey('right.id'), primary_key=True),
    db.Column('association_time', db.DateTime(), default=datetime.datetime.now)
)


class Right(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    creation_date = db.Column(db.DateTime(), default=datetime.datetime.now)
    modification_date = db.Column(db.DateTime(), default=datetime.datetime.now, onupdate=datetime.datetime.now)
    name = db.Column(db.String(80), unique=True, nullable=False)

    users = db.relationship('User', secondary=users_rights,
                            backref=db.backref('rights', lazy=True), lazy='subquery')

    def __repr__(self):
        return self.name

    @classmethod
    def create(cls, name):
        if cls.exists(name):
            raise ValueError('The right {} already exists.'.format(name))
        right = cls(name=name)
        db.session.add(right)
        return right

    def delete(self):
        db.session.delete(self)

    @classmethod
    def from_db(cls, name):
        return Right.query.filter_by(name=name).first()

    @classmethod
    def exists(cls, name):
        right = Right.query.filter_by(name=name).first()
        if right is None:
            return False
        return True
