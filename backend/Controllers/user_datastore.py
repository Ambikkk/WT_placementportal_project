from flask_security import SQLAlchemyUserDatastore
from .database import db
from .models import User, Role
#user_datastore is used to manage user and role data in the database. It provides methods for creating, updating, and querying users and roles, as well as handling authentication and authorization tasks.
#Without it 
# We would have to:
# Write SQL queries
# Manually create users
# Manually assign roles
# Handle password hashing
# Write extra logic


user_datastore=SQLAlchemyUserDatastore(db,User,Role)