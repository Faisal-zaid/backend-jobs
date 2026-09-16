from flask import Flask
from flask_restful import Api
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
import os
from pathlib import Path

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

# Explicitly load .env relative to this file's folder
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

# Retrieve DATABASE_URL
db_url = os.environ.get("DATABASE_URL")

if db_url:
    # Fix legacy 'postgres://' URLs from Render/Heroku for SQLAlchemy
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    print(f"--> [DATABASE]: Connected to remote database.")
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///jobconnect.db"
    print("--> [DATABASE]: DATABASE_URL not found. Falling back to local SQLite.")

# JWT configuration 
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "pro-blue-secret-99")

# --- INITIALIZATION ---
# Initialize database with app
db.init_app(app)
migrate = Migrate(app, db)

# Initialize password hashing
# Note: bcrypt is used inside routes/auth.py via generate_password_hash
bcrypt = Bcrypt(app)

# Initialize JWT manager
jwt = JWTManager(app)

# Enable CORS (Crucial for React frontend on different port)
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize Flask-RESTful API
api = Api(app)

# --- DATABASE SETUP ---
# This ensures tables are created with new columns if they don't exist
# with app.app_context():
#     # Force CASCADE drop on PostgreSQL to remove dependent foreign key tables (e.g., orders)
#     db.session.execute(db.text("DROP SCHEMA public CASCADE;"))
#     db.session.execute(db.text("CREATE SCHEMA public;"))
#     db.session.commit()
#     db.create_all()

# --- DATABASE SETUP ---
with app.app_context():
    # Creates missing tables safely without wiping existing user data
    db.create_all()
    
       

# --- ROUTES ---
@app.route("/")
def home():
    return {
        "status": "online",
        "message": "JobsConnect Professional API is running",
        "version": "1.1.0"
    }, 200

# Authentication
api.add_resource(Register, "/register")
api.add_resource(Login, "/login")

# Jobs Management
api.add_resource(JobsResource, "/jobs")
api.add_resource(JobResource, "/jobs/<int:id>")

# Applications
api.add_resource(ApplyJob, "/applications")
api.add_resource(EmployerApplications, "/employer/applications")

# Companies & Users
api.add_resource(CompaniesResource, "/companies")
api.add_resource(UsersResource, "/users")

#if __name__ == "__main__":
#    app.run(debug=True, port=5000)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)