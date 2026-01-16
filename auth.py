from flask_restful import Resource, reqparse
from models import User, db
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token

# ---------------------------
# Register parser
# ---------------------------
register_parser = reqparse.RequestParser(bundle_errors=True)
register_parser.add_argument("name", required=True, type=str, help="Name is required")
register_parser.add_argument("email", required=True, type=str, help="Email is required")
register_parser.add_argument("password", required=True, type=str, help="Password is required")
register_parser.add_argument("role", required=True, type=str, help="Role is required")

class Register(Resource):
    def post(self):
        try:
            data = register_parser.parse_args()

            # Check if user exists
            if User.query.filter_by(email=data["email"]).first():
                return {"message": "User already exists"}, 409

            # Hash password
            password_hash = generate_password_hash(data["password"]).decode("utf-8")
             # Create user
            user = User(
                name=data["name"],
                email=data["email"],
                password=password_hash,
                role=data["role"]
            )
            db.session.add(user)
            db.session.commit()
