import bcrypt
import string
import random


def hash_pw(clear_pw):
    encoded_pw = clear_pw.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(encoded_pw, salt)
    return hashed


def code_gen(size=6, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
