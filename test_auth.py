import requests
from leetcode_client import get_auth

query = """
{
  user {
    username
  }
}
"""
headers, cookies = get_auth()

response = requests.post(
    "https://leetcode.com/graphql",
    json = {"query" : query},
    headers = headers,
    cookies = cookies,
)

print(response.status_code)
print(response.json())