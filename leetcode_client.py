import os
import requests
from dotenv import load_dotenv
import time

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

def get_solved_problems():
    headers, cookies = get_auth()
    operationName = "problemsetQuestionListV2"
    variables = {
        "skip": 0,
        "limit": 100,
        "categorySlug": "all-code-essentials",
        "searchKeyword": "",
        "filters": {
            "filterCombineType": "ALL",
            "statusFilter": {
                "questionStatuses": [],
                "operator": "IS"
            }
        },
        "sortBy": {
            "sortField": "CUSTOM",
            "sortOrder": "ASCENDING"
        }
    }
    query = """
    \n    query problemsetQuestionListV2($filters: QuestionFilterInput, $limit: Int, $searchKeyword: String, $skip: Int, $sortBy: QuestionSortByInput, $categorySlug: String) {\n  problemsetQuestionListV2(\n    filters: $filters\n    limit: $limit\n    searchKeyword: $searchKeyword\n    skip: $skip\n    sortBy: $sortBy\n    categorySlug: $categorySlug\n  ) {\n    questions {\n      id\n      titleSlug\n      title\n      translatedTitle\n      questionFrontendId\n      paidOnly\n      difficulty\n      topicTags {\n        name\n        slug\n        nameTranslated\n      }\n      status\n      isInMyFavorites\n      frequency\n      acRate\n      contestPoint\n    }\n    totalLength\n    finishedLength\n    hasMore\n  }\n}\n
    """
    results = []
    while True:
        response = requests.post(
                "https://leetcode.com/graphql",
                json = {
                    "operationName": operationName,
                    "query": query,
                    "variables": variables
                },
                headers = headers,
                cookies = cookies,
            )
        response = response.json()
        for q in response['data']['problemsetQuestionListV2']['questions']:
            if q['status'] == "SOLVED":
                results.append(q)
        if not(response['data']['problemsetQuestionListV2']['hasMore']):
            break
        variables["skip"] += 100
        time.sleep(1)
    return results

def get_submissions_for_problem(questionSlug):
    operationName = "submissionList"
    headers, cookies = get_auth()
    query = """
    query submissionList($offset: Int!, $limit: Int!, $lastKey: String, $questionSlug: String!, $lang: Int, $status: Int) {\n  questionSubmissionList(\n    offset: $offset\n    limit: $limit\n    lastKey: $lastKey\n    questionSlug: $questionSlug\n    lang: $lang\n    status: $status\n  ) {\n    lastKey\n    hasNext\n    submissions {\n      id\n      title\n      titleSlug\n      status\n      statusDisplay\n      lang\n      langName\n      runtime\n      timestamp\n      url\n      isPending\n      memory\n      hasNotes\n      notes\n      flagType\n      frontendId\n      topicTags {\n        id\n      }\n    }\n  }\n}\n
    """
    variables = {
        "questionSlug": questionSlug,
        "offset": 0,
        "limit": 20,
        "lastKey": None
    }
    results = []
    while True:
        response = requests.post(
            "https://leetcode.com/graphql",
            headers = headers,
            cookies = cookies,
            json = {
                "query": query,
                "variables": variables,
                "operationName": operationName
            }
        )
        response = response.json()
        for s in response["data"]["questionSubmissionList"]["submissions"]:
            results.append(s)
        if not(response["data"]["questionSubmissionList"]["hasNext"]):
            break
        variables["offset"] += variables["limit"]
        time.sleep(0.8)
    return results