import os
import requests
from dotenv import load_dotenv

load_dotenv()

session_cookie = os.environ.get("LEETCODE_SESSION")
csrf_token = os.environ.get("csrftoken")

query = """
{
  user {
    username
  }
}
"""

headers = {
    "Content-Type": "application/json",
    "Referer": "https://leetcode.com",
    "x-csrftoken": csrf_token,
}

cookies = {
    "LEETCODE_SESSION": session_cookie,
    "csrftoken": csrf_token,
}

response = requests.post(
    "https://leetcode.com/graphql",
    json = {"query" : query},
    headers = headers,
    cookies = cookies,
)

print(response.status_code)
print(response.json())