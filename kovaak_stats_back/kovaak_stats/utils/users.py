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


def format_users_stats(stats):
    res = {
        "scenarii": [],
    }
    for stat in stats:
        if stat.scenario in res["scenarii"]:
            res[stat.scenario].append(stat.to_dict())
        else:
            res["scenarii"].append(stat.scenario)
            res[stat.scenario] = [stat.to_dict()]
    return res
