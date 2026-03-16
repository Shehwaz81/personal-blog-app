import os
from main import app, db, User
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

with app.app_context(): # let flask know we are working within the appp context
    password = generate_password_hash(os.getenv("PASSWORD"))
    username = os.getenv("USERNAME")

    admin_data = User(hash_key=password, username=username)

    db.session.add(admin_data)
    db.session.commit()
