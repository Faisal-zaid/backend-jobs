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
             # Create JWT token
            token = create_access_token(
                identity=user.id,
                additional_claims={"role": user.role}
            )

            return {
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "role": user.role
                },
                "access_token": token
            }, 201
        except Exception as e:
            print("Register error:", e)
            return {"message": "Registration failed", "error": str(e)}, 500
        # ---------------------------
# Login parser
# ---------------------------
login_parser = reqparse.RequestParser(bundle_errors=True)
login_parser.add_argument("email", required=True, type=str, help="Email is required")
login_parser.add_argument("password", required=True, type=str, help="Password is required")

class Login(Resource):
    def post(self):
        try:
            data = login_parser.parse_args()

            user = User.query.filter_by(email=data["email"]).first()
            if not user:
                return {"message": "Invalid email or password"}, 401

            # Verify password safely
            if not check_password_hash(user.password, data["password"]):
                return {"message": "Invalid email or password"}, 401

            token = create_access_token(
                identity=user.id,
                additional_claims={"role": user.role}
            )

            return {
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "role": user.role
                },
                "access_token": token
            }, 200
        except Exception as e:
            print("Login error:", e)
            return {"message": "Login failed", "error": str(e)}, 500