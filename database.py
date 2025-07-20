import psycopg2
import os

def create_user_table():
    conn = psycopg2.connect(os.environ["DATABASE_URL"], sslmode='require')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
