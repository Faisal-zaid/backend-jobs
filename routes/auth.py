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

# Set required=False and flexible types to prevent parsing crashes
register_parser.add_argument("age", required=False)
register_parser.add_argument("country", required=False, type=str)
register_parser.add_argument("phone", required=False, type=str)
register_parser.add_argument("phone_number", required=False, type=str)

class Register(Resource):
    def post(self):
        try:
            data = register_parser.parse_args()

            # Check if user already exists
            if User.query.filter_by(email=data["email"]).first():
                return {"message": "User already exists"}, 409

            # Safely parse age integer
            parsed_age = None
            if data.get("age") is not None and str(data["age"]).isdigit():
                parsed_age = int(data["age"])

            # Map phone field flexibly
            phone_val = data.get("phone") or data.get("phone_number") or ""

            # Hash password safely
            password_hash = generate_password_hash(data["password"]).decode("utf-8")

            # Format role string to match postgres enum expectations
            user_role = str(data["role"]).strip().lower()

            # Create user model instance
            user = User(
                name=data["name"],
                email=data["email"],
                password=password_hash,
                role=user_role,
                age=parsed_age,
                country=data.get("country"),
                phone_number=phone_val
            )

            db.session.add(user)
            db.session.commit()

            # Generate JWT token with stringified identity & claims
            token = create_access_token(
                identity=str(user.id),
                additional_claims={"role": str(user.role)}
            )

            return {
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "role": str(user.role),
                    "age": user.age,
                    "country": user.country
                },
                "access_token": token
            }, 201

        except Exception as e:
            db.session.rollback()
            print("Register exception caught:", str(e))
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
            if not user or not check_password_hash(user.password, data["password"]):
                return {"message": "Invalid email or password"}, 401

            token = create_access_token(
                identity=str(user.id),
                additional_claims={"role": str(user.role)}
            )

            return {
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "role": str(user.role),
                    "age": user.age,
                    "country": user.country
                },
                "access_token": token
            }, 200

        except Exception as e:
            print("Login exception caught:", str(e))
            return {"message": "Login failed", "error": str(e)}, 500