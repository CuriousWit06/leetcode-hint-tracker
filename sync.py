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
    submissions = leetcode_client.get_submissions_for_problem(problem['titleSlug'])
    for submission in submissions:
        cursor.execute("INSERT INTO submissions VALUES(%s, %s, %s, %s, %s) ON CONFLICT(id) DO NOTHING;", (submission['id'], problem['titleSlug'], submission['statusDisplay'], submission['lang'], submission['timestamp']))
    conn.commit()

cursor.close()
conn.close()