import leetcode_client
import psycopg2
from dotenv import load_dotenv
import os
import json
import time

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

problems = leetcode_client.get_solved_problems()
for problem in problems:
    cursor.execute("INSERT INTO problems VALUES(%s, %s, %s, %s, %s) ON CONFLICT(title_slug) DO NOTHING;", (problem['titleSlug'], problem['title'], problem['difficulty'], problem['status'], json.dumps(problem['topicTags'])))
    conn.commit()

cursor.close()
conn.close()