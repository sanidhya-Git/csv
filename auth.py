import psycopg2
import os

def get_connection():
    return psycopg2.connect(os.environ["DATABASE_URL"], sslmode='require')

def signup_user(email, password):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, password))
        conn.commit()
        return True
    except psycopg2.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(email, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def reset_password(email, new_password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    if cursor.fetchone() is None:
        conn.close()
        return False

    cursor.execute("UPDATE users SET password = %s WHERE email = %s", (new_password, email))
    conn.commit()
    conn.close()
    return True
