from flask_restful import Resource, reqparse
from models import Company, db
import traceback

company_parser = reqparse.RequestParser(bundle_errors=True)
company_parser.add_argument("name", required=True, type=str, help="Company name is required")
company_parser.add_argument("location", required=False, type=str)

company_update_parser = reqparse.RequestParser(bundle_errors=True)
company_update_parser.add_argument("name", required=False, type=str)
company_update_parser.add_argument("location", required=False, type=str)


class CompaniesResource(Resource):
    def get(self):
        try:
            companies = Company.query.all()
            return [company.to_dict() for company in companies], 200
        except Exception as e:
            print("\n==================== GET COMPANIES ERROR ====================")
            traceback.print_exc()
            print("=============================================================\n")
            return {"message": "Failed to fetch companies", "error": str(e)}, 500

    def post(self):
        try:
            data = company_parser.parse_args()

            existing = Company.query.filter_by(name=data["name"]).first()
            if existing:
                return {"message": "Company already exists"}, 409

            company = Company(
                name=data["name"],
                location=data.get("location")
            )

            db.session.add(company)
            db.session.commit()

            return company.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            print("\n==================== CREATE COMPANY ERROR ====================")
            traceback.print_exc()
            print("==============================================================\n")
            return {"message": "Failed to create company", "error": str(e)}, 500

    def put(self):
        try:
            data = company_update_parser.parse_args()

            if not data.get("name"):
                return {"message": "Company name is required for update"}, 400

            company = Company.query.filter_by(name=data["name"]).first()
            if not company:
                return {"message": "Company not found"}, 404

            if data.get("location") is not None:
                company.location = data["location"]

            db.session.commit()
            return company.to_dict(), 200
        except Exception as e:
            db.session.rollback()
            print("\n==================== UPDATE COMPANY ERROR ====================")
            traceback.print_exc()
            print("==============================================================\n")
            return {"message": "Failed to update company", "error": str(e)}, 500

    def delete(self):
        try:
            data = company_update_parser.parse_args()

            if not data.get("name"):
                return {"message": "Company name is required for deletion"}, 400

            company = Company.query.filter_by(name=data["name"]).first()
            if not company:
                return {"message": "Company not found"}, 404

            company_data = company.to_dict()
            db.session.delete(company)
            db.session.commit()

            return {"message": "Company deleted successfully", "company": company_data}, 200
        except Exception as e:
            db.session.rollback()
            print("\n==================== DELETE COMPANY ERROR ====================")
            traceback.print_exc()
            print("==============================================================\n")
            return {"message": "Failed to delete company", "error": str(e)}, 500