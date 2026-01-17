from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Job, Company, db, User

# -------------------------
# REQUEST PARSER
# -------------------------
job_parser = reqparse.RequestParser()
job_parser.add_argument("title", required=True, type=str, help="Title is required")
job_parser.add_argument("description", required=True, type=str, help="Description is required")
job_parser.add_argument(
    "job_type", required=True, type=str,
    choices=("remote", "hybrid", "physical"),
    help="Job type is required"
)
job_parser.add_argument("education", required=True, type=str, help="Education is required")
job_parser.add_argument("company_name", required=True, type=str, help="Company name is required")
job_parser.add_argument("salary_min", type=int)
job_parser.add_argument("salary_max", type=int)
job_parser.add_argument("location", type=str)

# -------------------------
# JOBS RESOURCE
# -------------------------
class JobsResource(Resource):
    @jwt_required()
    def get(self):
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                return {"message": "User not found"}, 404

            if user.role == "employer":
                # Only return jobs posted by this employer
                jobs = Job.query.filter_by(employer_id=user.id).all()
            else:
                # Job seeker sees all jobs
                jobs = Job.query.all()

            return [job.to_dict() for job in jobs], 200

        except Exception as e:
            print("Get Jobs error:", e)
            return {"message": "Failed to fetch jobs", "error": str(e)}, 500

    @jwt_required()
    def post(self):
        try:
            data = job_parser.parse_args()

            # Get current employer from JWT
            employer_id = get_jwt_identity()
            employer = User.query.get(employer_id)
            if not employer or employer.role != "employer":
                return {"message": "Unauthorized: only employers can add jobs"}, 403

            # Get or create company
            company = Company.query.filter_by(name=data["company_name"]).first()
            if not company:
                company = Company(name=data["company_name"])
                db.session.add(company)
                db.session.commit()

            # Create job
            job = Job(
                title=data["title"],
                description=data["description"],
                job_type=data["job_type"],
                education=data["education"],
                company_id=company.id,
                employer_id=employer.id,
                salary_min=data.get("salary_min"),
                salary_max=data.get("salary_max"),
                location=data.get("location")
            )

            db.session.add(job)
            db.session.commit()

            return {"message": "Job added successfully", "job": job.to_dict()}, 201

        except Exception as e:
            print("Add Job error:", e)
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
            print("Get Job error:", e)
            return {"message": "Failed to fetch job", "error": str(e)}, 500

    @jwt_required()
    def delete(self, id):
        try:
            employer_id = get_jwt_identity()
            job = Job.query.get_or_404(id)

            # Only allow the owner to delete
            if job.employer_id != employer_id:
                return {"message": "Unauthorized: cannot delete this job"}, 403

            db.session.delete(job)
            db.session.commit()
            return {"message": "Job deleted successfully"}, 200

        except Exception as e:
            print("Delete Job error:", e)
            return {"message": "Failed to delete job", "error": str(e)}, 500