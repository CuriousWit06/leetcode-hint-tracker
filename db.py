from dotenv import load_dotenv
import os
import psycopg2

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

def create_db():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS problems(title_slug TEXT PRIMARY KEY, title TEXT NOT NULL, difficulty TEXT NOT NULL, status TEXT, topic_tags JSONB);
    CREATE TABLE IF NOT EXISTS submissions(id BIGINT PRIMARY KEY, title_slug TEXT NOT NULL REFERENCES problems(title_slug), status_display TEXT NOT NULL, lang TEXT, submitted_at BIGINT);
    CREATE TABLE IF NOT EXISTS submission_details(submission_id BIGINT PRIMARY KEY REFERENCES submissions(id), code TEXT, code_output TEXT, expected_output TEXT, last_testcase TEXT, runtime_error TEXT, compile_error TEXT);
    """)

    conn.commit()
    cursor.close()
    conn.close()