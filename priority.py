import os
from dotenv import load_dotenv
import psycopg2
import time

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_details():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("SELECT p.title_slug, p.title, p.difficulty, COUNT(CASE WHEN s.status_display != 'Accepted' THEN 1 END) AS attempts_before_ac, MAX(s.submitted_at) as last_accept_timestamp FROM problems p INNER JOIN submissions s on p.title_slug = s.title_slug GROUP BY (p.title_slug, p.title, p.difficulty);")
    result = cursor.fetchall()

    cursor.close()
    conn.close()
    return result

def get_due_problems():
    rows = get_details()

    present = time.time()
    result = []

    for row in rows:
        title_slug, title, difficulty, attempts_before_ac, last_accept_timestamp = row

        days_since_last = (present - last_accept_timestamp) // 86400
        score = compute_score(attempts_before_ac, difficulty, days_since_last)

        result.append([title_slug, title, score, difficulty])

    result.sort(key = lambda x: x[2], reverse = True)
    return result

def compute_score(attempts_before_ac, difficulty, days_since_last):
    diff = {
        "EASY": 1,
        "MEDIUM": 2,
        "HARD": 3
    }
    w_diff = 2.2

    tim = None
    if 0 <= days_since_last <= 9:
        tim = 1
    elif 10 <= days_since_last <= 20:
        tim = 1.2
    elif 21 <= days_since_last <= 29:
        tim = 1.5
    elif 30 <= days_since_last <= 90:
        tim = 2
    elif 90 < days_since_last <= 180:
        tim = 3
    else:
        tim = 3.8
    w_time = 1.5

    atmpts = None
    if attempts_before_ac <= 1:
        atmpts = 0.8
    elif 2 <= attempts_before_ac <= 3:
        atmpts = 1.3
    elif 3 < attempts_before_ac <= 5:
        atmpts = 1.7
    elif 5 < attempts_before_ac <= 10:
        atmpts = 2.1
    else:
        atmpts = 2.5
    w_attempts = 3.1

    return ((w_attempts * atmpts) + (w_time * tim) + (w_diff * diff[difficulty]))