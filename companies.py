from flask_restful import Resource, reqparse
from models import Company, db

company_parser = reqparse.RequestParser()
company_parser.add_argument("name", required=True, type=str)
company_parser.add_argument("location", required=False, type=str)

# Parser for PUT requests (all fields optional)
company_update_parser = reqparse.RequestParser()
company_update_parser.add_argument("name", required=False, type=str)
company_update_parser.add_argument("location", required=False, type=str)


class CompaniesResource(Resource):
    def get(self):
        """Get all companies"""
        companies = Company.query.all()
        return [company.to_dict() for company in companies], 200

    def post(self):
        """Create a new company"""
        data = company_parser.parse_args()

        # Prevent duplicates
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

    def put(self):
        """Update an existing company by name"""
        data = company_update_parser.parse_args()

        # Require name to identify the company
        if not data.get("name"):
            return {"message": "Company name is required for update"}, 400

        company = Company.query.filter_by(name=data["name"]).first()
        if not company:
            return {"message": "Company not found"}, 404

        # Update fields if provided
        if data.get("location") is not None:
            company.location = data["location"]

        # Check if trying to change name to an existing company's name
        if data.get("name") and data["name"] != company.name:
            existing = Company.query.filter_by(name=data["name"]).first()
            if existing:
                return {"message": "A company with that name already exists"}, 409
            company.name = data["name"]

        db.session.commit()
        return company.to_dict(), 200

    def delete(self):
        """Delete a company by name"""
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
