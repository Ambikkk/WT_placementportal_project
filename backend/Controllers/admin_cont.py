from flask_restful import Resource
from flask_security import auth_token_required
from flask import request
from .models import Company, Student, Job, Application, User
from .database import db



class AdminDashboardAPI(Resource):

    @auth_token_required
    def get(self):
        return {
            "total_students": Student.query.count(),
            "total_companies": Company.query.count(),
            "total_jobs": Job.query.count(),
            "total_applications": Application.query.count(),

            "recent_registrations": [
                {
                    "id": u.id,
                    "email": u.email,
                    "roles": [r.name for r in u.roles]
                }
                for u in User.query.order_by(User.id.desc()).limit(5)
            ]
        }



class ManageStudentsAPI(Resource):

    @auth_token_required
    def get(self):
        return [
            {
                "id": s.id,
                "name": s.name,
                "branch": s.branch,
                "cgpa": s.cgpa,
                "status": s.status
            }
            for s in Student.query.all()
        ]



class ManageCompaniesAPI(Resource):

    @auth_token_required
    def get(self):
        return [
            {
                "id": c.id,
                "name": c.name,
                "location": c.location,
                "status": c.status
            }
            for c in Company.query.all()
        ]



class ApproveCompanyAPI(Resource):

    @auth_token_required
    def post(self):
        data = request.get_json()
        company = Company.query.get(data.get('id'))

        if not company:
            return {"msg": "Company not found"}, 404

        company.status = "active"
        db.session.commit()

        return {"msg": "Approved"}


class BlacklistCompanyAPI(Resource):

    @auth_token_required
    def post(self):
        data = request.get_json()
        company = Company.query.get(data.get('id'))

        if not company:
            return {"msg": "Company not found"}, 404

        company.status = "blacklisted"
        db.session.commit()

        return {"msg": "Blacklisted"}



class UnblacklistCompanyAPI(Resource):

    @auth_token_required
    def post(self):
        data = request.get_json()
        company = Company.query.get(data.get('id'))

        if not company:
            return {"msg": "Company not found"}, 404

        company.status = "active"
        db.session.commit()

        return {"msg": "Unblacklisted"}


class BlacklistStudentAPI(Resource):

    @auth_token_required
    def post(self):
        data = request.get_json()
        student = Student.query.get(data.get('id'))

        if not student:
            return {"msg": "Student not found"}, 404

        student.status = "blacklisted"
        db.session.commit()

        return {"msg": "Student blacklisted"}
    
class UnblacklistStudentAPI(Resource):

    @auth_token_required
    def post(self):
        data = request.get_json()
        student_id = data.get('id')

        student = Student.query.get(student_id)

        if not student:
            return {"msg": "Student not found"}, 404

        student.status = "active"
        db.session.commit()

        return {"msg": "Student unblacklisted"}
class StudentDetailAPI(Resource):

    @auth_token_required
    def get(self, user_id):

        student = Student.query.filter_by(user_id=user_id).first()

        if not student:
            return {"msg": "Student not found"}, 404

        applications = Application.query.filter_by(student_id=student.id).all()

        return {
            "name": student.name,
            "branch": student.branch,
            "cgpa": student.cgpa,
            "status": student.status,

            "applications": [
                {
                    "job": a.job.title,
                    "company": a.job.company.name,
                    "status": a.status
                }
                for a in applications
            ]
        }
class CompanyDetailAPI(Resource):

    @auth_token_required
    def get(self, user_id):

        company = Company.query.filter_by(user_id=user_id).first()

        if not company:
            return {"msg": "Company not found"}, 404

        jobs = Job.query.filter_by(company_id=company.id).all()

        return {
            "name": company.name,
            "location": company.location,
            "status": company.status,

            "jobs": [
                {
                    "title": j.title,
                    "salary": j.salary,
                    "applications": len(Application.query.filter_by(job_id=j.id).all())
                }
                for j in jobs
            ]
        }

class ManageDrivesAPI(Resource):
    @auth_token_required
    def get(self):
        jobs = Job.query.all()
        return [
            {
                "id": j.id,
                "title": j.title,
                "company": j.company.name if j.company else "Unknown",
                "salary": j.salary,
                "deadline": j.deadline.strftime('%Y-%m-%d') if j.deadline else None,
                "status": j.status,
                "applications": Application.query.filter_by(job_id=j.id).count()
            }
            for j in jobs
        ]

class ApproveJobAPI(Resource):
    @auth_token_required
    def post(self, job_id):
        job = Job.query.get(job_id)
        if not job:
            return {"msg": "Job not found"}, 404
        job.status = "active"
        db.session.commit()
        return {"msg": "Approved"}

class RejectJobAPI(Resource):
    @auth_token_required
    def post(self, job_id):
        job = Job.query.get(job_id)
        if not job:
            return {"msg": "Job not found"}, 404
        job.status = "rejected"
        db.session.commit()
        return {"msg": "Rejected"}