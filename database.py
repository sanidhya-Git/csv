import os
import psycopg2
import bcrypt
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in environment variables")


ADMIN_EMAIL = "admin@csv.com"
ADMIN_PASSWORD = "admin@123"


@contextmanager
def conn():
    connection = psycopg2.connect(
        DATABASE_URL,
        sslmode="require"
    )

    try:
        yield connection
        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def hash_password(password):
    return bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    ).decode()


def init_db():
    with conn() as db:
        cur = db.cursor()

        # USERS TABLE
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            email TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            plan TEXT DEFAULT 'free'
        )
        """)

        # UPLOADS TABLE
        cur.execute("""
        CREATE TABLE IF NOT EXISTS uploads(
            id SERIAL PRIMARY KEY,
            email TEXT NOT NULL,
            filename TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # commit safe point
        db.commit()

        # old migration safely
        try:
            cur.execute("""
            ALTER TABLE users
            RENAME COLUMN password TO password_hash
            """)
            db.commit()
        except:
            db.rollback()

        # add column safely
        try:
            cur.execute("""
            ALTER TABLE users
            ADD COLUMN IF NOT EXISTS plan TEXT DEFAULT 'free'
            """)
            db.commit()
        except:
            db.rollback()

        # admin create
        try:
            cur.execute(
                """
                SELECT email FROM users
                WHERE LOWER(email)=LOWER(%s)
                """,
                ("admin@csv.com",)
            )

            if not cur.fetchone():

                admin_hash = hash_password("admin@123")

                cur.execute(
                    """
                    INSERT INTO users(email,password_hash,plan)
                    VALUES(%s,%s,%s)
                    """,
                    (
                        "admin@csv.com",
                        admin_hash,
                        "pro"
                    )
                )
                db.commit()

        except:
            db.rollback()
def create_user(email, password_hash):
    try:
        with conn() as db:
            cur = db.cursor()

            cur.execute(
                """
                INSERT INTO users(email,password_hash)
                VALUES(%s,%s)
                """,
                (
                    email.strip().lower(),
                    password_hash
                )
            )

        return True, "Account created successfully"

    except psycopg2.errors.UniqueViolation:
        return False, "User already exists"

    except Exception as e:
        return False, f"Signup failed: {e}"


def fetch_password_hash(email):
    with conn() as db:
        cur = db.cursor()

        cur.execute(
            """
            SELECT password_hash
            FROM users
            WHERE LOWER(email)=LOWER(%s)
            """,
            (email.strip(),)
        )

        row = cur.fetchone()

        return row[0] if row else None


def get_user(email):
    with conn() as db:
        cur = db.cursor(
            cursor_factory=RealDictCursor
        )

        cur.execute(
            """
            SELECT email,plan
            FROM users
            WHERE LOWER(email)=LOWER(%s)
            """,
            (email.strip(),)
        )

        return cur.fetchone()


def record_upload(email, filename):
    with conn() as db:
        cur = db.cursor()

        cur.execute(
            """
            INSERT INTO uploads(email,filename)
            VALUES(%s,%s)
            """,
            (
                email.strip().lower(),
                filename
            )
        )


def monthly_upload_count(email):
    with conn() as db:
        cur = db.cursor()

        cur.execute(
            """
            SELECT COUNT(*)
            FROM uploads
            WHERE LOWER(email)=LOWER(%s)
            AND date_trunc('month',created_at)
            = date_trunc('month',CURRENT_TIMESTAMP)
            """,
            (email.strip(),)
        )

        row = cur.fetchone()

        return row[0] if row else 0


def update_user_plan(email, plan):
    with conn() as db:
        cur = db.cursor()

        cur.execute(
            """
            UPDATE users
            SET plan=%s
            WHERE LOWER(email)=LOWER(%s)
            """,
            (
                plan.strip().lower(),
                email.strip()
            )
        )


def total_users():
    with conn() as db:
        cur = db.cursor()

        cur.execute(
            "SELECT COUNT(*) FROM users"
        )

        row = cur.fetchone()

        return row[0] if row else 0