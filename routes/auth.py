from flask_restful import Resource, reqparse
from models import User, db
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token

# ---------------------------
# Register parser - Updated with new fields
# ---------------------------
register_parser = reqparse.RequestParser(bundle_errors=True)
register_parser.add_argument("name", required=True, type=str, help="Name is required")
register_parser.add_argument("email", required=True, type=str, help="Email is required")
register_parser.add_argument("password", required=True, type=str, help="Password is required")
register_parser.add_argument("role", required=True, type=str, help="Role is required")

# 🔹 ADDED NEW FIELDS
register_parser.add_argument("age", required=True, type=int, help="Age is required and must be an integer")
register_parser.add_argument("country", required=True, type=str, help="Country is required")
register_parser.add_argument("phone", required=True, type=str, help="Phone number is required")

class Register(Resource):
    def post(self):
        try:
            data = register_parser.parse_args()

            # Check if user exists
            if User.query.filter_by(email=data["email"]).first():
                return {"message": "User already exists"}, 409

            # Hash password
            password_hash = generate_password_hash(data["password"]).decode("utf-8")
            
            # 🔹 Create user with new fields
            user = User(
                name=data["name"],
                email=data["email"],
                password=password_hash,
                role=data["role"],
                age=data["age"],
                country=data["country"],
                phone_number=data["phone"] # Mapping 'phone' from React to 'phone_number' in DB
            )
            
            db.session.add(user)
            db.session.commit()

            # Create JWT token
            token = create_access_token(
                identity=str(user.id),
                additional_claims={"role": str(user.role)}
            )

            return {
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "role": user.role,
                    "age": user.age,
                    "country": user.country
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
                    "role": user.role,
                    "age": user.age,      # 🔹 Added for frontend profile context
                    "country": user.country
                },
                "access_token": token
            }, 200
        except Exception as e:
            print("Login error:", e)
            return {"message": "Login failed", "error": str(e)}, 500