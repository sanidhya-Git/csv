import bcrypt
from database import create_user, fetch_password_hash

def signup_user(email, password):
    hashed = bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    ).decode()

    return create_user(email, hashed)

def login_user(email, password):
    stored = fetch_password_hash(email)

    if not stored:
        return False

    return bcrypt.checkpw(
        password.encode(),
        stored.encode()
    )