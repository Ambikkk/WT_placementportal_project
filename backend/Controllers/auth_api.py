from flask_restful import Resource
from flask import make_response,request, jsonify
from .user_datastore import user_datastore
from .models import User, Role, Student, Company
from .database import db
from flask_security import utils,auth_token_required
from flask_login import login_user, logout_user, current_user   

import uuid



class LoginAPI(Resource):
    def post(self):
        data=request.get_json()
        email=data.get('email')
        password=data.get('password')
        if email is None or password is None:
            return make_response(jsonify({'message':'Email and password both are required'}),400)
        else:
            find=user_datastore.find_user(email=email)
            if not find:
                return make_response(jsonify({'message':'User not found','done':False}),404) 
            else:

                if not  utils.verify_password(password, find.password):
                    return make_response(jsonify({'message':'Invalid password'}),401)
                else:
                    #here find.password is the hashed password stored in the database and password is the plain text password provided by the user during login. The verify_password function hashes the provided password and compares it with the stored hash to check if they match.
                    login_user(find)
                    token=find.get_auth_token()
                    db.session.commit()
                    message={
                        'token':token,
                        'message':'Login successful',
                        'done':True,
                        'user_details':{
                            'email':find.email,
                            'id':find.id
                        }
                    }
                    return make_response(jsonify(message),200)
                    
                
        
class LogoutAPI(Resource):
    @auth_token_required
    def post(self):
        user=current_user
        # user.fs_token_uniquifier=utils.hash_password(str(user.id))
        # Generates new random value
        # Ensures old token becomes invalid
        # Safe and standard

        user.fs_token_uniquifier=str(uuid.uuid4()) #all random random values
        logout_user()
        db.session.commit()
        return make_response(jsonify({'message':'Logout successful','done':True}),200)
    

    
class RegisterAPI(Resource):
    def post(self):
        data = request.get_json()

        email = data.get('email')
        password = data.get('password')
        role = data.get('role')

        if email is None or password is None or role is None:
            return make_response(jsonify({'message': 'Email, password and role required'}), 400)

        if user_datastore.find_user(email=email):
            return make_response(jsonify({'message': 'User already exists'}), 400)

        role_obj = user_datastore.find_role(role)

        if role_obj is None:
            return make_response(jsonify({'message': 'Invalid role'}), 400)

        user = user_datastore.create_user(
            email=email,
            password=password,
            roles=[role_obj]
        )

        user_datastore.commit()

        
        if role == 'student':
            student_profile = Student(
                user_id=user.id,
                name=data.get('name'),
                branch=data.get('branch'),
                cgpa=data.get('cgpa')
            )
            db.session.add(student_profile)

        
        elif role == 'company':
            company_profile = Company(
                user_id=user.id,
                name=data.get('name'),
                description=data.get('description'),
                location=data.get('location')
            )
            db.session.add(company_profile)

        db.session.commit()

        return make_response(jsonify({
            'message': f'{role.capitalize()} registered successfully'
        }), 201)