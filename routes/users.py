from flask_restful import Resource
from flask_jwt_extended import jwt_required
from models import User

class UsersResource(Resource):
    #@jwt_required()
    def get(self):
        return [user.to_dict() for user in User.query.all()], 200