from flask import Blueprint
from flask_restplus import Api

from kovaak_stats.api.users import api as ns_users
from kovaak_stats.api.rights import api as ns_rights

api_bp = Blueprint('api', __name__)
api = Api(api_bp, version='0.0', title='Kovaak stats viewer API',
          description='API used by the kovaak stats viewer frontend',
          doc='/doc')
api.add_namespace(ns_users)
api.add_namespace(ns_rights)
