from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Application, Job, User, db
import traceback

class ApplyJob(Resource):
    @jwt_required()
    def post(self):
        try:
            raw_identity = get_jwt_identity()
            user_id = int(raw_identity) if str(raw_identity).isdigit() else raw_identity
            
            data = request.get_json()
            if not data:
                return {"message": "No input data provided"}, 400

            required_fields = ["job_id", "applicant_name", "education", "cv", "cover_letter"]
            missing = [f for f in required_fields if not data.get(f)]
            if missing:
                return {"message": {f: f"{f.replace('_', ' ').capitalize()} is required" for f in missing}}, 400

            job = Job.query.get(data["job_id"])
            if not job:
                return {"message": "Job not found"}, 404

            application = Application(
                user_id=user_id,
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
                "application": application.to_dict()
            }, 201

        except Exception as e:
            db.session.rollback()
            print("\n==================== APPLY JOB ERROR ====================")
            traceback.print_exc()
            print("=========================================================\n")
            return {"message": "Failed to submit application", "error": str(e)}, 500


class EmployerApplications(Resource):
    @jwt_required()
    def get(self):
        try:
            raw_identity = get_jwt_identity()
            employer_id = int(raw_identity) if str(raw_identity).isdigit() else raw_identity

            query_results = db.session.query(
                Application, 
                User.age, 
                User.country, 
                User.phone_number
            ).join(User, Application.user_id == User.id)\
             .join(Job, Application.job_id == Job.id)\
             .filter(Job.employer_id == employer_id)\
             .order_by(Application.applied_at.desc()).all()

            if not query_results:
                return {"applications": [], "message": "No applications found"}, 200

            formatted_apps = []
            for app, age, country, phone in query_results:
                formatted_apps.append({
                    "id": app.id,
                    "applicant_name": app.applicant_name,
                    "education": app.education,
                    "cv": app.cv,
                    "cover_letter": app.cover_letter,
                    "job_id": app.job_id,
                    "job_title": app.job.title if app.job else "Unknown Position",
                    "applied_at": app.applied_at.strftime("%b %d, %Y") if app.applied_at else None,
                    "age": age,
                    "country": country,
                    "phone_number": phone
                })

            return {
                "count": len(formatted_apps),
                "applications": formatted_apps
            }, 200

        except Exception as e:
            print("\n==================== GET APPLICATIONS ERROR ====================")
            traceback.print_exc()
            print("=================================================================\n")
            return {"message": "Error fetching applications", "error": str(e)}, 500