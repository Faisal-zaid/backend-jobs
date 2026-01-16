from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime

metadata = MetaData()
db = SQLAlchemy(metadata=metadata)



# -------------------------
# USERS (KEEP FOR LATER)
# -------------------------
class User(db.Model, SerializerMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    role = db.Column(db.Enum("job_seeker", "employer"), nullable=False)

    serialize_rules = ("-password",)


# -------------------------
# COMPANIES
# -------------------------
class Company(db.Model, SerializerMixin):
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    location = db.Column(db.Text)

    jobs = db.relationship("Job", back_populates="company", cascade="all, delete-orphan")

    serialize_rules = ("-jobs.company",)

