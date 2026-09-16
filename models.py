from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime

metadata = MetaData()
db = SQLAlchemy(metadata=metadata)


# -------------------------
# USERS MODEL
# -------------------------
class User(db.Model, SerializerMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    role = db.Column(db.Enum("job_seeker", "employer", name="user_role_enum"), nullable=False)

    age = db.Column(db.Integer, nullable=True)
    country = db.Column(db.Text, nullable=True)
    phone_number = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    applications = db.relationship("Application", back_populates="applicant", cascade="all, delete-orphan")
    jobs_posted = db.relationship("Job", back_populates="employer", cascade="all, delete-orphan")

    serialize_rules = ("-password", "-created_at", "-applications.applicant", "-jobs_posted.employer")


# -------------------------
# COMPANIES MODEL
# -------------------------
class Company(db.Model, SerializerMixin):
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    location = db.Column(db.Text)

    jobs = db.relationship("Job", back_populates="company", cascade="all, delete-orphan")

    serialize_rules = ("-jobs.company",)


# -------------------------
# JOBS MODEL
# -------------------------
class Job(db.Model, SerializerMixin):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    job_type = db.Column(db.Text, nullable=False)
    education = db.Column(db.Text, nullable=False)

    salary_min = db.Column(db.Integer, nullable=True)
    salary_max = db.Column(db.Integer, nullable=True)
    location = db.Column(db.Text, nullable=True)

    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    employer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    company = db.relationship("Company", back_populates="jobs")
    employer = db.relationship("User", back_populates="jobs_posted")
    applications = db.relationship(
        "Application",
        back_populates="job",
        cascade="all, delete-orphan"
    )

    serialize_rules = (
        "-company.jobs",
        "-employer.jobs_posted",
        "-applications.job",
    )


# -------------------------
# APPLICATIONS MODEL
# -------------------------
class Application(db.Model, SerializerMixin):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    applicant_name = db.Column(db.Text, nullable=True)
    education = db.Column(db.Text, nullable=True)
    cv = db.Column(db.Text, nullable=False)
    cover_letter = db.Column(db.Text, nullable=True)

    applied_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)

    job = db.relationship("Job", back_populates="applications")
    applicant = db.relationship("User", back_populates="applications")

    serialize_rules = ("-job.applications", "-applicant.applications")