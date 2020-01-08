from kovaak_stats.app import db

users_rights = db.Table(
    'users_rights',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('right_id', db.Integer, db.ForeignKey('right.id'), primary_key=True)
)


class Right(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    users = db.relationship('User', secondary=users_rights,
                            backref=db.backref('rights', lazy=True), lazy='subquery')

    def __repr__(self):
        return self.name

    @classmethod
    def create(cls, name):
        right = cls(name=name)
        db.session.add(right)
        return right

    @classmethod
    def from_db(cls, name):
        return Right.query.filter_by(name=name).first()
