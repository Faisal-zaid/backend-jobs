from flask import Flask
from flask_restful import Api
from flask_migrate import Migrate

# Flask-Bcrypt for password hashing
from flask_bcrypt import Bcrypt

# Flask-JWT-Extended for authentication with JWTs
from flask_jwt_extended import JWTManager

#Flask-CORS to allow frontend-backend communication
from flask_cors import CORS

# Load environment variables from .env file
from dotenv import load_dotenv
import os

# Import API resource classes
from models import db
from routes.auth import Register, Login
from routes.jobs import JobsResource, JobResource
from routes.applications import ApplyJob, EmployerApplications
from routes.companies import CompaniesResource
from routes.users import UsersResource

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///jobconnect.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# JWT configuration 
app.config["JWT_SECRET_KEY"] = os.environ.get(
    "JWT_SECRET_KEY", "super-secret"
)

# Initialize database with app
db.init_app(app)
Migrate(app, db)

# Initialize password hashing
bcrypt = Bcrypt(app)

# Initialize JWT manager
jwt = JWTManager()
jwt.init_app(app)
