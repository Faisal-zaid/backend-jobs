from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Job, Company, db, User
import traceback

# -------------------------
# REQUEST PARSER
# -------------------------
job_parser = reqparse.RequestParser(bundle_errors=True)
job_parser.add_argument("title", required=True, type=str, help="Title is required")
job_parser.add_argument("description", required=True, type=str, help="Description is required")
job_parser.add_argument(
    "job_type", required=True, type=str,
    choices=("remote", "hybrid", "physical"),
    help="Job type must be 'remote', 'hybrid', or 'physical'"
)
job_parser.add_argument("education", required=True, type=str, help="Education is required")
job_parser.add_argument("company_name", required=True, type=str, help="Company name is required")
job_parser.add_argument("salary_min", required=False)
job_parser.add_argument("salary_max", required=False)
job_parser.add_argument("location", required=False, type=str)


# -------------------------
# JOBS RESOURCE
# -------------------------
class JobsResource(Resource):
    @jwt_required()
    def get(self):
        try:
            raw_identity = get_jwt_identity()
            user_id = int(raw_identity) if str(raw_identity).isdigit() else raw_identity

            user = User.query.get(user_id)
            if not user:
                return {"message": "User not found"}, 404

            if str(user.role).strip().lower() == "employer":
                # Only return jobs posted by this employer
                jobs = Job.query.filter_by(employer_id=user.id).all()
            else:
                # Job seeker sees all jobs
                jobs = Job.query.all()

            return [job.to_dict() for job in jobs], 200

        except Exception as e:
            print("\n==================== GET JOBS ERROR ====================")
            traceback.print_exc()
            print("========================================================\n")
            return {"message": "Failed to fetch jobs", "error": str(e)}, 500

    @jwt_required()
    def post(self):
        try:
            data = job_parser.parse_args()

            # Safely cast employer_id from JWT identity string
            raw_identity = get_jwt_identity()
            try:
                employer_id = int(raw_identity)
            except (ValueError, TypeError):
                return {"message": "Invalid JWT identity format"}, 422

            # Verify employer privileges
            employer = User.query.get(employer_id)
            if not employer or str(employer.role).strip().lower() != "employer":
                return {"message": "Unauthorized: only employers can add jobs"}, 403

            # Find or create company
            company = Company.query.filter_by(name=data["company_name"]).first()
            if not company:
                company = Company(
                    name=data["company_name"],
                    location=data.get("location")
                )
                db.session.add(company)
                db.session.commit()

            # Parse numeric salaries safely
            salary_min = int(data["salary_min"]) if data.get("salary_min") and str(data["salary_min"]).isdigit() else None
            salary_max = int(data["salary_max"]) if data.get("salary_max") and str(data["salary_max"]).isdigit() else None

            # Create new job
            job = Job(
                title=data["title"],
                description=data["description"],
                job_type=data["job_type"],
                education=data["education"],
                company_id=company.id,
                employer_id=employer.id,
                salary_min=salary_min,
                salary_max=salary_max,
                location=data.get("location")
            )

            db.session.add(job)
            db.session.commit()

            return {
                "message": "Job added successfully",
                "job": job.to_dict()
            }, 201

        except Exception as e:
            db.session.rollback()
            print("\n==================== POST JOB ERROR ====================")
            traceback.print_exc()
            print("========================================================\n")
            return {"message": "Failed to add job", "error": str(e)}, 500


# -------------------------
# SINGLE JOB RESOURCE
# -------------------------
class JobResource(Resource):
    @jwt_required()
    def get(self, id):
        try:
            job = Job.query.get_or_404(id)
            return job.to_dict(), 200
        except Exception as e:
            print("\n==================== GET SINGLE JOB ERROR ====================")
            traceback.print_exc()
            print("==============================================================\n")
            return {"message": "Failed to fetch job", "error": str(e)}, 500

    @jwt_required()
    def delete(self, id):
        try:
            raw_identity = get_jwt_identity()
            employer_id = int(raw_identity) if str(raw_identity).isdigit() else raw_identity
            
            job = Job.query.get_or_404(id)

            # Ensure only creator deletes the post
            if job.employer_id != employer_id:
                return {"message": "Unauthorized: cannot delete this job"}, 403

            db.session.delete(job)
            db.session.commit()
            return {"message": "Job deleted successfully"}, 200

        except Exception as e:
            db.session.rollback()
            print("\n==================== DELETE JOB ERROR ====================")
            traceback.print_exc()
            print("==========================================================\n")
            return {"message": "Failed to delete job", "error": str(e)}, 500