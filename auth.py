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