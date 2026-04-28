from datetime import datetime, timedelta
import csv
from io import StringIO
import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from app import app


from celery_app import celery


from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


from Controllers.models import Job, Application, Student, User, Company
from Controllers.config import config



def _send_message(recipients, subject, body):
    try:
        message = Mail(
            from_email=os.getenv("FROM_EMAIL"),
            to_emails=recipients,
            subject=subject,
            html_content=body
        )

        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        sg.send(message)

        print(f"Email sent to {recipients}")

    except Exception as e:
        print(" SendGrid error:", e)



def send_email(to_email, job, type="apply"):

    if type == "new_job":
        subject = f"New Job Opportunity: {job.title}"
        body = f"""
        <p>Hello,</p>

        <p>A new job opportunity has been posted:</p>

        <ul>
            <li><b>Position:</b> {job.title}</li>
            <li><b>Company:</b> {job.company.name}</li>
            <li><b>Salary:</b> {job.salary or "Not disclosed"}</li>
            <li><b>Minimum CGPA:</b> {job.min_cgpa}</li>
            <li><b>Branch:</b> {job.branch or "All branches"}</li>
            <li><b>Deadline:</b> {job.deadline.strftime('%Y-%m-%d')}</li>
            <li><b>Location:</b> {job.company.location}</li>
        </ul>

        <p>Please log in to the portal and apply before the deadline.</p>
        """

    elif type == "apply":
        subject = f"Application Submitted Successfully - {job.title}"
        body = f"""
        <p>Hello,</p>

        <p>Your application for <b>{job.title}</b> at <b>{job.company.name}</b> has been successfully submitted.</p>

        <p>You will be notified regarding further updates.</p>
        """

    elif type == "accepted":
        subject = f"Congratulations! You are Selected for {job.title}"
        body = f"""
        <p>Hello,</p>

        <p><b>Congratulations!</b></p>

        <p>You have been selected for <b>{job.title}</b> at <b>{job.company.name}</b>.</p>

        <p>Please check your portal for further instructions.</p>
        """

    elif type == "deadline":
        subject = f"Reminder: Application Deadline Approaching - {job.title}"
        body = f"""
        <p>Hello,</p>

        <p>This is a reminder that the application deadline for <b>{job.title}</b> is approaching.</p>

        <p>Please apply as soon as possible to avoid missing this opportunity.</p>
        """

    else:
        subject = "Placement Notification"
        body = "<p>There is an update regarding your application. Please check the portal.</p>"

    _send_message([to_email], subject, body)



def get_student_email(student):
    if not student or not getattr(student, 'user_id', None):
        return None

    user = User.query.get(student.user_id)
    return getattr(user, 'email', None)



@celery.task
def send_daily_reminders():
    with app.app_context():
        print("🔔 Running daily reminders...")

        now = datetime.utcnow()
        cutoff = now + timedelta(days=3)

        jobs = Job.query.filter(
            Job.status == "active",
            Job.deadline >= now,
            Job.deadline <= cutoff
        ).all()

        students = Student.query.all()

        for job in jobs:
            for student in students:
                already_applied = Application.query.filter_by(
                    student_id=student.id,
                    job_id=job.id
                ).first()

                if already_applied:
                    continue

                email = get_student_email(student)
                if email:
                    send_email(email, job, "deadline")



@celery.task
def send_new_job_notifications(job_id):
    with app.app_context():
        job = Job.query.get(job_id)
        if not job:
            return

        students = Student.query.all()

        for student in students:
            already_applied = Application.query.filter_by(
                student_id=student.id,
                job_id=job.id
            ).first()

            if already_applied:
                continue

            email = get_student_email(student)
            if email:
                send_email(email, job, "new_job")



@celery.task
def send_email_async(to_email, job_id, type="apply"):
    with app.app_context():
        print("🔥 TASK RUNNING", to_email, job_id, type)

        job = Job.query.get(job_id)
        if job:
            send_email(to_email, job, type)
        else:
            print(" Job not found")



@celery.task
def monthly_report():
    with app.app_context():
        applications = Application.query.all()
        total = len(applications)

        report = f"""
        Monthly Report<br><br>
        Total Applications: {total}
        """

        _send_message(
            [getattr(config, 'ADMIN_REPORT_EMAIL', 'admin@gmail.com')],
            "Monthly Report",
            report
        )


#
@celery.task
def export_applications(user_id):
    with app.app_context():
        user = User.query.get(user_id)
        if not user:
            return

        applications = Application.query.all()

        output = StringIO()
        writer = csv.writer(output)

        writer.writerow(["Student ID", "Company", "Job", "Status"])

        for app_obj in applications:
            writer.writerow([
                app_obj.student.id if app_obj.student else '',
                app_obj.job.company.name if app_obj.job and app_obj.job.company else '',
                app_obj.job.title if app_obj.job else '',
                app_obj.status
            ])

        _send_message(
            [user.email],
            "Applications Export",
            "Your export is ready."
        )
