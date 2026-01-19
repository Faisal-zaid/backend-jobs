from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Application, Job, db

# -------------------------
# JOB SEEKER: SUBMIT APPLICATION
# -------------------------
class ApplyJob(Resource):
    def post(self):
        try:
            data = request.get_json()
            if not data:
                return {"message": "No input data provided"}, 400

            # Validation
            required_fields = ["job_id", "applicant_name", "education", "cv", "cover_letter"]
            missing = [f for f in required_fields if not data.get(f)]
            if missing:
                return {"message": {f: f"{f.replace('_', ' ').capitalize()} is required" for f in missing}}, 400

            # Check job exists
            job = Job.query.get(data["job_id"])
            if not job:
                return {"message": "Job not found"}, 404

            application = Application(
                applicant_name=data["applicant_name"],
                education=data["education"],
                cv=data["cv"],
                cover_letter=data["cover_letter"],
                job_id=data["job_id"]
            )

            db.session.add(application)
            db.session.commit()

            return {
                "message": "Application submitted successfully",
                "application": application.to_dict() # Assumes SerializerMixin is in models
            }, 201

        except Exception as e:
            db.session.rollback()
            return {"message": "Failed to submit application", "error": str(e)}, 500


# EMPLOYER: VIEW RECEIVED APPLICATIONS

class EmployerApplications(Resource):
    @jwt_required()
    def get(self):
        try:
            # Identity from the JWT token (Employer's ID)
            employer_id = get_jwt_identity()
            
            # 1. Find all jobs belonging to this employer
            employer_jobs = Job.query.filter_by(employer_id=employer_id).all()
            job_ids = [job.id for job in employer_jobs]

            if not job_ids:
                return {"applications": []}, 200

            # 2. Get applications for those specific jobs
            applications = Application.query.filter(
                Application.job_id.in_(job_ids)
            ).all()

            return {
                "applications": [
                    {
                        "id": app.id,
                        "applicant_name": app.applicant_name,
                        "education": app.education,
                        "cv": app.cv,
                        "cover_letter": app.cover_letter,
                        "job_id": app.job_id,
                        "job_title": app.job.title if app.job else "N/A",
                        "submitted_at": app.created_at.strftime("%Y-%m-%d") if hasattr(app, 'created_at') else None
                    } for app in applications
                ]
            }, 200

        except Exception as e:
            return {"message": "Error fetching applications", "error": str(e)}, 500