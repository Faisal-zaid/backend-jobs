from flask_restful import Resource
from flask_jwt_extended import jwt_required
from models import User
import traceback

class UsersResource(Resource):
    @jwt_required()
    def get(self):
        try:
            users = User.query.all()
            return [user.to_dict() for user in users], 200
        except Exception as e:
            print("\n==================== GET USERS ERROR ====================")
            traceback.print_exc()
            print("=========================================================\n")
            return {"message": "Failed to fetch users", "error": str(e)}, 500