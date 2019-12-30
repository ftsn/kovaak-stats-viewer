import bcrypt


def user_list():
    from kovaak_stats.models.user import User
    return User.query.all()


def hash_pw(clear_pw):
    encoded_pw = clear_pw.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(encoded_pw, salt)
    return hashed
