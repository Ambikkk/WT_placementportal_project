from flask_restful import Resource
from flask_security import auth_token_required, current_user
from flask import Response
import csv
from io import StringIO
from Controllers.models import Application


class ExportCSVAPI(Resource):

    @auth_token_required
    def get(self):

        applications = Application.query.all()

        output = StringIO()
        writer = csv.writer(output)

        writer.writerow(["Student", "Company", "Job", "Status"])

        for app in applications:
            writer.writerow([
                app.student.name,
                app.job.company.name,
                app.job.title,
                app.status
            ])

        output.seek(0)

        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=applications.csv"
            }
        )
    

from flask_restful import Resource
from flask_security import auth_token_required, current_user
from flask import Response
import csv
from io import StringIO
from Controllers.models import Application, Student


class StudentExportCSVAPI(Resource):

    @auth_token_required
    def get(self):

        student = Student.query.filter_by(user_id=current_user.id).first()

        if not student:
            return {"msg": "Student not found"}, 404

        applications = Application.query.filter_by(student_id=student.id).all()

        output = StringIO()
        writer = csv.writer(output)

        writer.writerow(["Job Title", "Company", "Salary", "Status", "Deadline"])

        for app in applications:
            writer.writerow([
                app.job.title,
                app.job.company.name,
                app.job.salary,
                app.status,
                app.job.deadline.strftime('%Y-%m-%d') if app.job.deadline else ""
            ])

        output.seek(0)

        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=my_applications.csv"
            }
        )
    
from flask_restful import Resource
from flask_security import auth_token_required, current_user
from flask import Response
import csv
from io import StringIO
from Controllers.models import Application, Company, Job


class ExportCCSVAPI(Resource):

    @auth_token_required
    def get(self):

        company = Company.query.filter_by(user_id=current_user.id).first()

        if not company:
            return {"msg": "Company not found"}, 404

        # ✅ Get only this company’s jobs
        jobs = Job.query.filter_by(company_id=company.id).all()
        job_ids = [job.id for job in jobs]

        # ✅ Get applications only for those jobs
        applications = Application.query.filter(
            Application.job_id.in_(job_ids)
        ).all()

        output = StringIO()
        writer = csv.writer(output)

        writer.writerow(["Student", "Branch", "CGPA", "Job", "Status"])

        for app in applications:
            writer.writerow([
                app.student.name,
                app.student.branch,
                app.student.cgpa,
                app.job.title,
                app.status
            ])

        output.seek(0)

        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=company_applications.csv"
            }
        )