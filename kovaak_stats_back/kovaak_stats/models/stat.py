from kovaak_stats.app import db
import datetime


class Stat(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    creation_date = db.Column(db.DateTime(), default=datetime.datetime.now)
    modification_date = db.Column(db.DateTime(), default=datetime.datetime.now, onupdate=datetime.datetime.now)
    execution_date = db.Column(db.DateTime())
    filename = db.Column(db.String(200), unique=True, nullable=False)
    kills_info = db.Column(db.JSON)
    weapon = db.Column(db.String(80), nullable=False)
    total_accuracy = db.Column(db.Float, nullable=False)
    shots = db.Column(db.Integer, nullable=False)
    hits = db.Column(db.Integer, nullable=False)
    damage_done = db.Column(db.Float, nullable=False)
    damage_possible = db.Column(db.Float, nullable=False)
    kills = db.Column(db.Integer, nullable=False)
    deaths = db.Column(db.Integer, nullable=False)
    fight_time = db.Column(db.Float, nullable=False)
    avg_ttk = db.Column(db.Float, nullable=False)
    damage_taken = db.Column(db.Float, nullable=False)
    midairs = db.Column(db.Integer, nullable=False)
    midaired = db.Column(db.Integer, nullable=False)
    directs = db.Column(db.Integer, nullable=False)
    directed = db.Column(db.Integer, nullable=False)
    distance_traveled = db.Column(db.Float, nullable=False)
    score = db.Column(db.Float, nullable=False)
    scenario = db.Column(db.String(80), nullable=False)
    scenario_hash = db.Column(db.String(80), nullable=False)
    game_version = db.Column(db.String(80), nullable=False)
    input_lag = db.Column(db.Integer, nullable=False)
    max_fps = db.Column(db.Float, nullable=False)
    sens_scale = db.Column(db.String(80), nullable=False)
    horiz_sens = db.Column(db.Float, nullable=False)
    vert_sens = db.Column(db.Float, nullable=False)
    fov = db.Column(db.Float, nullable=False)
    hide_gun = db.Column(db.Boolean, nullable=False)
    crosshair = db.Column(db.String(80), nullable=False)
    crosshair_scale = db.Column(db.Float, nullable=False)
    crosshair_color = db.Column(db.String(80), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return self.filename

    @classmethod
    def create(cls, file, user):
        stat = cls()
        lines = file.read().decode('utf-8').splitlines()
        stat.filename = file.filename
        stat.execution_date = gen_execution_date(stat.filename)

        stat.kills_info = gen_kills_info(lines)
        stat.weapon, stat.shots, stat.hits, stat.damage_done, stat.damage_possible = gen_dmg_info(lines)
        (stat.kills, stat.deaths, stat.fight_time, stat.avg_ttk, stat.damage_taken, stat.midairs, stat.midaired,
         stat.directs, stat.directed, stat.distance_traveled, stat.score, stat.scenario, stat.scenario_hash,
         stat.game_version, stat.input_lag, stat.max_fps, stat.sens_scale, stat.horiz_sens, stat.vert_sens, stat.fov,
         stat.hide_gun, stat.crosshair, stat.crosshair_scale, stat.crosshair_color) = gen_other_info(lines)
        stat.total_accuracy = (stat.hits / stat.shots) * 100
        if cls.exists(stat.filename):
            raise ValueError('The stat file {} has already been uploaded.'.format(stat.filename))
        db.session.add(stat)
        user.stats.append(stat)
        return stat

    @classmethod
    def exists(cls, filename):
        stat = cls.query.filter_by(filename=filename).first()
        return stat is not None

    def to_dict(self):
        return {
            'creation_date': str(self.creation_date),
            'modification_date': str(self.modification_date),
            'execution_date': str(self.execution_date),
            'filename': self.filename,
            'kills_info': self.kills_info,
            'weapon': self.weapon,
            'total_accuracy': self.total_accuracy,
            'shots': self.shots,
            'hits': self.hits,
            'damage_done': self.damage_done,
            'damage_possible': self.damage_possible,
            'kills': self.kills,
            'deaths': self.deaths,
            'fight_time': self.fight_time,
            'avg_ttk': self.avg_ttk,
            'damage_taken': self.damage_taken,
            'midairs': self.midairs,
            'midaired': self.midaired,
            'directs': self.directs,
            'directed': self.directed,
            'distance_traveled': self.distance_traveled,
            'score': self.score,
            'scenario': self.scenario,
            'scenario_hash': self.scenario_hash,
            'game_version': self.game_version,
            'input_lag': self.input_lag,
            'max_fps': self.max_fps,
            'sens_scale': self.sens_scale,
            'horiz_sens': self.horiz_sens,
            'vert_sens': self.vert_sens,
            'fov': self.fov,
            'hide_gun': self.hide_gun,
            'crosshair': self.crosshair,
            'crosshair_scale': self.crosshair_scale,
            'crosshair_color': self.crosshair_color,
        }

def gen_kills_info(lines):
    info_list = None
    details = False
    for line in lines:
        if line.startswith("Kill #"):
            info_list = []
            details = True
            continue
        if line == '':
            break
        if details:
            cur_info = line.split(',')
            info_list.append({
                'number': int(cur_info[0]),
                'time': cur_info[1],
                'bot_type': cur_info[2],
                'weapon': cur_info[3],
                'ttk': cur_info[4],
                'shots': int(cur_info[5]),
                'hits': int(cur_info[6]),
                'accuracy': float(cur_info[7]),
                'damage_done': float(cur_info[8]),
                'damage_possible': float(cur_info[9]),
                'cheated': True if cur_info[10] == 'true' else False
            })
    return info_list


def gen_dmg_info(lines):
    info_list = None
    details = False
    for line in lines:
        if line.startswith("Weapon"):
            details = True
            continue
        if details:
            cur_info = line.split(',')
            info_list = [
                cur_info[0],
                int(cur_info[1]),
                int(cur_info[2]),
                float(cur_info[3]),
                float(cur_info[4])
            ]
            break
    return info_list


def gen_other_info(lines):
    info_list = []
    identifiers = [
        {'str': 'Kills:', 'convert': int},
        {'str': 'Deaths:', 'convert': int},
        {'str': 'Fight Time:', 'convert': float},
        {'str': 'Avg TTK:', 'convert': float},
        {'str': 'Damage Taken:', 'convert': float},
        {'str': 'Midairs:', 'convert': int},
        {'str': 'Midaired:', 'convert': int},
        {'str': 'Directs:', 'convert': int},
        {'str': 'Directed:', 'convert': int},
        {'str': 'Distance Traveled:', 'convert': float},
        {'str': 'Score:', 'convert': float},
        {'str': 'Scenario:', 'convert': None},
        {'str': 'Hash:', 'convert': None},
        {'str': 'Game Version:', 'convert': None},
        {'str': 'Input Lag:', 'convert': int},
        {'str': 'Max FPS (config):', 'convert': float},
        {'str': 'Sens Scale:', 'convert': None},
        {'str': 'Horiz Sens:', 'convert': float},
        {'str': 'Vert Sens:', 'convert': float},
        {'str': 'FOV:', 'convert': float},
        {'str': 'Hide Gun:', 'convert': lambda x: True if x == 'true' else False},
        {'str': 'Crosshair:', 'convert': None},
        {'str': 'Crosshair Scale:', 'convert': float},
        {'str': 'Crosshair Color:', 'convert': None},
    ]
    for line in lines:
        split_line = line.split(',')
        for identifier in identifiers:
            if line.startswith(identifier['str']):
                if identifier['convert']:
                    info_list.append(identifier['convert'](split_line[1]))
                else:
                    info_list.append(split_line[1])
                break
    return info_list


def gen_execution_date(filename):
    splitted = filename.split(' ')
    splitted_raw_datetime = splitted[len(splitted) - 2].split('-')
    formatted = '{} {}'.format(splitted_raw_datetime[0].replace('.', '-'), splitted_raw_datetime[1].replace('.', ':'))
    return datetime.datetime.strptime(formatted, '%Y-%m-%d %H:%M:%S')
