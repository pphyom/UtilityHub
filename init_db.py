
from werkzeug.security import generate_password_hash
from models.models import User
from main.extensions import db
from app import app

# Predefined users
predefined_users = [
    {"username": "admin", "password": "admin123"},
    {"username": "user1", "password": "password1"},
    {"username": "user2", "password": "password2"}
]


def init_db():
    """
    Initialize the database with the predefined users.

    This function creates all database tables and adds predefined users to the database
    if they do not already exist. It uses the predefined_users list to get the user data.

    Usage:
        Call this function to set up the initial state of the database with default users.
    """
    
    db.create_all()
    try:
        for user in predefined_users:
            if not User.query.filter_by(username=user["username"]).first():
                new_user = User(username=user["username"],
                                password=generate_password_hash(user["password"]))
                db.session.add(new_user)
        db.session.commit()
        print("Database initialized!")
    except Exception as e:
        db.session.rollback()
        print(f"An error occurred: {e}")
        

if __name__ == "__main__":
    with app.app_context():
        init_db()