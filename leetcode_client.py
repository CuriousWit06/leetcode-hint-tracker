import os
from dotenv import load_dotenv

load_dotenv()

def get_auth():
    session_cookie = os.environ.get("LEETCODE_SESSION")
    csrftoken = os.environ.get("csrftoken")

    headers = {
        "Content-Type": "application/json",
        "Referer": "https://leetcode.com",
        "x-csrftoken": csrftoken,
    }

    cookies = {
        "LEETCODE_SESSION": session_cookie,
        "csrftoken": csrftoken,
    }
    return headers, cookies