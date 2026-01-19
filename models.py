from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime

metadata = MetaData()
db = SQLAlchemy(metadata=metadata)

# -------------------------
# USERS
# -------------------------
class User(db.Model, SerializerMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    role = db.Column(db.Enum("job_seeker", "employer"), nullable=False)

    # 🔹 NEW FIELDS FOR REGISTRATION
    age = db.Column(db.Integer, nullable=True)
    country = db.Column(db.Text, nullable=True)
    phone_number = db.Column(db.Text, nullable=True)

    # Automatically track when the user joined
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Serialization rules to hide sensitive info
    serialize_rules = ("-password", "-created_at")


# -------------------------
# COMPANIES
# -------------------------
class Company(db.Model, SerializerMixin):
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    location = db.Column(db.Text)

    # Relationship to Jobs
    jobs = db.relationship("Job", back_populates="company", cascade="all, delete-orphan")

    serialize_rules = ("-jobs.company",)


# -------------------------
# JOBS
# -------------------------
class Job(db.Model, SerializerMixin):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    job_type = db.Column(db.Text, nullable=False) # e.g., 'Remote', 'Full-time'
    education = db.Column(db.Text, nullable=False)

    # Financial and Location details
    salary_min = db.Column(db.Integer, nullable=True)
    salary_max = db.Column(db.Integer, nullable=True)
    location = db.Column(db.Text, nullable=True)

    # Foreign Keys
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    employer_id = db.Column(db.Integer, nullable=False) # Tracks which user posted it

    # Relationships
    company = db.relationship("Company", back_populates="jobs")
    applications = db.relationship(
        "Application",
        back_populates="job",
        cascade="all, delete-orphan"
    )

    serialize_rules = (
        "-company.jobs",
        "-applications.job",
    )

# -------------------------
# APPLICATIONS
# -------------------------
class Application(db.Model, SerializerMixin):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    applicant_name = db.Column(db.Text, nullable=True)
    education = db.Column(db.Text, nullable=True)
    cv = db.Column(db.Text, nullable=False) # Store path or base64 string
    cover_letter = db.Column(db.Text, nullable=True) 

    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Connection to the Job
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    job = db.relationship("Job", back_populates="applications")

    serialize_rules = ("-job.applications",)