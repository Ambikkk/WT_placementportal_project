from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from flask_security import Security
from flask_mail import Mail
from flask_caching import Cache
from sqlalchemy import text

from Controllers.config import config
from Controllers.database import db
from Controllers.user_datastore import user_datastore
from dotenv import load_dotenv
load_dotenv()
# extensions
mail = Mail()
cache = Cache()


def upgrade_sqlite_schema(app):
    with app.app_context():
        inspector = db.inspect(db.engine)
        existing_tables = inspector.get_table_names()

        def add_column(table, column_name, column_sql):
            if table not in existing_tables:
                return
            columns = [col['name'] for col in inspector.get_columns(table)]
            if column_name not in columns:
                db.session.execute(text(f'ALTER TABLE {table} ADD COLUMN {column_sql}'))
                db.session.commit()

        add_column('student', 'created_at', 'created_at DATETIME')
        add_column('student', 'resume_filename', 'resume_filename VARCHAR(255)')
        add_column('company', 'created_at', 'created_at DATETIME')
        add_column('job', 'created_at', 'created_at DATETIME')
        add_column('application', 'created_at', 'created_at DATETIME')


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    # init extensions
    db.init_app(app)
    mail.init_app(app)
    cache.init_app(app)

    security = Security(app, user_datastore)
    api = Api(app, prefix='/api')
    CORS(app, supports_credentials=True)

    # import routes INSIDE function (important)
    from Controllers.auth_api import LoginAPI, LogoutAPI, RegisterAPI
    from Controllers.student_cont import (
        StudentDashboardAPI, MyApplicationsAPI,
        StudentProfileAPI, StudentJobsAPI,
        ApplyJobAPI
    )
    from Controllers.company_cont import (
        CompanyDashboardAPI, PostJobAPI,
        CompanyApplicationsAPI, UpdateApplicationStatusAPI
    )
    from Controllers.admin_cont import (
        AdminDashboardAPI, ManageCompaniesAPI, ManageStudentsAPI,
        ApproveCompanyAPI, BlacklistCompanyAPI, BlacklistStudentAPI,
        UnblacklistCompanyAPI, UnblacklistStudentAPI,
        StudentDetailAPI, CompanyDetailAPI,
        ManageDrivesAPI, ApproveJobAPI, RejectJobAPI
    )
    from Controllers.export_api import ExportCSVAPI, StudentExportCSVAPI,ExportCCSVAPI


    # routes
    api.add_resource(LoginAPI, '/login')
    api.add_resource(LogoutAPI, '/logout')
    api.add_resource(RegisterAPI, '/register')

    api.add_resource(StudentDashboardAPI, '/student_dashboard')
    api.add_resource(MyApplicationsAPI, "/student/applications")
    api.add_resource(StudentProfileAPI, "/student/profile")
    api.add_resource(StudentJobsAPI, '/student/jobs')
    api.add_resource(ApplyJobAPI, '/student/apply/<int:job_id>')
    # api.add_resource(StudentCacheAPI, '/student_cache')
    # api.add_resource(UploadResumeAPI, '/student/resume/upload')
    # api.add_resource(DownloadResumeAPI, '/student/resume/download')
    # api.add_resource(AdminCompanyDownloadResumeAPI, '/student/resume/download/<int:student_id>')

    api.add_resource(CompanyDashboardAPI, '/company_dashboard')
    api.add_resource(PostJobAPI, '/post_job')
    api.add_resource(CompanyApplicationsAPI, "/company/applications")
    api.add_resource(UpdateApplicationStatusAPI, "/company/application/<int:app_id>")

    api.add_resource(AdminDashboardAPI, '/admin_dashboard')
    # api.add_resource(SearchCompaniesAPI, '/search/companies')
    # api.add_resource(SearchJobsAPI, '/search/jobs')

    api.add_resource(ManageStudentsAPI, '/manage_students')
    api.add_resource(ManageCompaniesAPI, '/manage_companies')

    api.add_resource(ApproveCompanyAPI, '/approve_company')
    api.add_resource(BlacklistCompanyAPI, '/blacklist_company')
    api.add_resource(UnblacklistCompanyAPI, '/unblacklist_company')

    api.add_resource(BlacklistStudentAPI, '/blacklist_student')
    api.add_resource(UnblacklistStudentAPI, '/unblacklist_student')

    api.add_resource(StudentDetailAPI, '/admin/student/<int:user_id>')
    api.add_resource(CompanyDetailAPI, '/admin/company/<int:user_id>')

    api.add_resource(ManageDrivesAPI, '/admin/manage_drives')
    api.add_resource(ApproveJobAPI, '/admin/approve_job/<int:job_id>')
    api.add_resource(RejectJobAPI, '/admin/reject_job/<int:job_id>')

    api.add_resource(ExportCSVAPI, '/export')
    api.add_resource(StudentExportCSVAPI, "/student/export")
    api.add_resource(ExportCCSVAPI, "/company/export")


    # DB setup and schema migrations for older database files
    with app.app_context():
        upgrade_sqlite_schema(app)
        db.create_all()

        admin_role = user_datastore.find_or_create_role(name='admin')
        student_role = user_datastore.find_or_create_role(name='student')
        company_role = user_datastore.find_or_create_role(name='company')

        if not user_datastore.find_user(email='admin@gmail.com'):
            user_datastore.create_user(
                email='admin@gmail.com',
                password='admin123',
                roles=[admin_role]
            )

        db.session.commit()

    return app, api


# create app
app, api = create_app()


if __name__ == '__main__':
    app.run(debug=True)