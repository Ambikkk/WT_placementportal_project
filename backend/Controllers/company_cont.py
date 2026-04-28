from flask_restful import Resource
from flask_security import auth_token_required, current_user
from flask import request
from datetime import datetime, timedelta
from .models import db, Company, Job, Application


class CompanyDashboardAPI(Resource):

    @auth_token_required
    def get(self):
        user = current_user
        company = Company.query.filter_by(user_id=user.id).first()

        if not company:
            return {"msg": "Company not found"}, 404

        jobs = Job.query.filter_by(company_id=company.id).all()
        total_apps = 0
        job_list = []

        for job in jobs:
            apps = Application.query.filter_by(job_id=job.id).all()
            total_apps += len(apps)

            job_list.append({
                "job_id": job.id,
                "title": job.title,
                "salary": job.salary,
                "deadline": job.deadline.strftime('%Y-%m-%d') if job.deadline else None,
                "applications": len(apps)
            })

        return {
            "company_name": company.name,
            "total_jobs": len(jobs),
            "total_applications": total_apps,
            "jobs": job_list
        }


class PostJobAPI(Resource):

    @auth_token_required
    def post(self):
        user = current_user
        company = Company.query.filter_by(user_id=user.id).first()

        if not company:
            return {"msg": "Company not found"}, 404

        data = request.get_json() or {}

        title = data.get("title")

        
        try:
            salary = float(data.get("salary"))
        except:
            return {"msg": "Salary must be a number"}, 400

        deadline_str = data.get("deadline")

        if not title:
            return {"msg": "Missing title"}, 400

        deadline = None
        if deadline_str:
            try:
                deadline = datetime.fromisoformat(deadline_str)
            except ValueError:
                return {"msg": "Invalid deadline format"}, 400

        if not deadline:
            deadline = datetime.utcnow() + timedelta(days=10)

        job = Job(
            company_id=company.id,
            title=title,
            salary=salary,  # ✅ now correct
            min_cgpa=data.get("min_cgpa"),
            branch=data.get("branch"),
            description=data.get("description"),
            deadline=deadline,
            status="pending"
        )

        db.session.add(job)
        db.session.commit()

        try:
            from Controllers.tasks import send_new_job_notifications
            try:
                send_new_job_notifications.delay(job.id)
            except Exception as task_error:
                print("Celery enqueue failed, sending emails synchronously:", task_error)
                send_new_job_notifications(job.id)
        except Exception as e:
            print("Email sending ERROR:", e)

        return {"msg": "Job posted successfully"}, 201

class CompanyApplicationsAPI(Resource):

    @auth_token_required
    def get(self):
        user = current_user
        company = Company.query.filter_by(user_id=user.id).first()

        if not company:
            return {"msg": "Company not found"}, 404

        jobs = Job.query.filter_by(company_id=company.id).all()
        data = []

        for job in jobs:
            apps = Application.query.filter_by(job_id=job.id).all()
            for app in apps:
                data.append({
                    "app_id": app.id,
                    "job_id": job.id,
                    "job_title": job.title,
                    "student_id": app.student.id,
                    "student_name": app.student.name,
                    "branch": app.student.branch,
                    "cgpa": app.student.cgpa,
                    "status": app.status
                })

        return data


class UpdateApplicationStatusAPI(Resource):

    @auth_token_required
    def post(self, app_id):
        data = request.get_json() or {}
        status = data.get("status")

        app = Application.query.get(app_id)
        if not app:
            return {"msg": "Not found"}, 404

        app.status = status
        db.session.commit()

        
        if status in ["accepted", "selected"]:
            from Controllers.tasks import send_email_async
            from Controllers.models import User

            user = User.query.get(app.student.user_id)

            if user and user.email:
                print("🔥 SENDING ACCEPTED EMAIL")
                send_email_async.delay(user.email, app.job.id, "accepted")

        return {"msg": "Updated"}


class CompanyDetailAPI(Resource):

    @auth_token_required
    def get(self, user_id):
        company = Company.query.filter_by(user_id=user_id).first()
        if not company:
            return {"msg": "Company not found"}, 404

        jobs = Job.query.filter_by(company_id=company.id).all()
        job_data = []

        for job in jobs:
            applications = Application.query.filter_by(job_id=job.id).all()
            job_data.append({
                "title": job.title,
                "salary": job.salary,
                "deadline": job.deadline.strftime('%Y-%m-%d') if job.deadline else None,
                "status": job.status,
                "applications": [
                    {
                        "student_name": app.student.name,
                        "branch": app.student.branch,
                        "cgpa": app.student.cgpa,
                        "status": app.status
                    }
                    for app in applications
                ]
            })

        return {
            "company_name": company.name,
            "location": company.location,
            "status": company.status,
            "jobs": job_data
        }
