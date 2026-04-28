
from datetime import datetime
from flask_restful import Resource
from flask_security import auth_token_required, current_user
from flask import request, current_app
from .models import Student, Job, Application, Company, User
from .database import db


def clear_cache(student_id):
    cache = current_app.extensions.get('cache')
    if cache and hasattr(cache, "delete"):
        cache.delete(f"student_dashboard_{student_id}")


class StudentDashboardAPI(Resource):
    @auth_token_required
    def get(self):
        student = Student.query.filter_by(user_id=current_user.id).first()
        if not student:
            return {"msg": "Student not found"}, 404

        applications = Application.query.filter_by(student_id=student.id).all()

        data = [
            {
                "job_title": app.job.title,
                "company": app.job.company.name,
                "salary": app.job.salary,
                "status": app.status,
                "applied_date": app.created_at.strftime('%Y-%m-%d %H:%M') if app.created_at else None
            }
            for app in applications
        ]

        return {
            "name": student.name,
            "branch": student.branch,
            "cgpa": student.cgpa,
            "total_applications": len(applications),
            "applications": data
        }



class MyApplicationsAPI(Resource):
    @auth_token_required
    def get(self):
        student = Student.query.filter_by(user_id=current_user.id).first()

        apps = Application.query.filter_by(student_id=student.id).all()

        return [
            {
                "job_title": app.job.title,
                "company": app.job.company.name,
                "salary": app.job.salary,
                "status": app.status,
                "applied_date": app.created_at.strftime('%Y-%m-%d %H:%M') if app.created_at else None
            }
            for app in apps
        ]



class StudentProfileAPI(Resource):
    @auth_token_required
    def get(self):
        student = Student.query.filter_by(user_id=current_user.id).first()
        if not student:
            return {"name": "", "branch": "", "cgpa": ""}, 200

        return {
            "name": student.name or "",
            "branch": student.branch or "",
            "cgpa": student.cgpa or "",
            "resume_filename": student.resume_filename or ""
        }, 200

    @auth_token_required
    def post(self):
        student = Student.query.filter_by(user_id=current_user.id).first()
        if not student:
            return {"msg": "Student not found"}, 404

        data = request.get_json() or {}
        student.name = data.get("name")
        student.branch = data.get("branch")
        student.cgpa = data.get("cgpa")

        db.session.commit()

        clear_cache(student.id)

        return {"msg": "Profile updated"}, 200



class StudentJobsAPI(Resource):
    @auth_token_required
    def get(self):
        now = datetime.utcnow()
        jobs = Job.query.filter(Job.status == "active", Job.deadline >= now).all()

        return [
            {
                "job_id": job.id,
                "title": job.title,
                "salary": job.salary,
                "company": job.company.name,
                "min_cgpa": job.min_cgpa,
                "branch": job.branch,
                "deadline": job.deadline.strftime('%Y-%m-%d'),
                "description": job.description,
                "location": job.company.location
            }
            for job in jobs
        ]



class ApplyJobAPI(Resource):
    @auth_token_required
    def post(self, job_id):
        print("🔥 APPLY API CALLED")

        from Controllers.tasks import send_email_async

        student = Student.query.filter_by(user_id=current_user.id).first()
        if not student:
            return {"msg": "Student not found"}, 404

        if student.status == "blacklisted":
            return {"msg": "Student is blacklisted"}, 403

        job = Job.query.get(job_id)
        if not job or job.status != "active":
            return {"msg": "Job not available"}, 404

        if job.deadline < datetime.utcnow():
            return {"msg": "Deadline has passed"}, 400

        existing = Application.query.filter_by(
            student_id=student.id,
            job_id=job_id
        ).first()

        if existing:
            return {"msg": "Already applied"}, 400

        # ✅ Save application
        app_obj = Application(student_id=student.id, job_id=job_id, status="applied")
        db.session.add(app_obj)
        db.session.commit()

        # ✅ Send email
        user = User.query.get(student.user_id)
        print("🔥 BEFORE CELERY CALL")
        print("EMAIL:", user.email if user else None)

        if user and user.email:
            send_email_async.delay(user.email, job.id)

        # ✅ Clear cache safely
        clear_cache(student.id)

        return {"msg": "Applied successfully"}

