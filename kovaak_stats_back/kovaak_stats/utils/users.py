import bcrypt


def hash_pw(clear_pw):
    encoded_pw = clear_pw.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(encoded_pw, salt)
    return hashed
