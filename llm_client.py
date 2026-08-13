from openai import OpenAI
from dotenv import load_dotenv
import psycopg2
import os

load_dotenv()

client = OpenAI(
    base_url = "https://router.huggingface.co/v1",
    api_key = os.environ.get("HF_TOKEN")
)

def get_hint(title_slug, level, previous_hints):
    DATABASE_URL = os.environ.get("DATABASE_URL")

    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("SELECT s.id, s.status_display, s.lang, s.submitted_at, sd.code, sd.code_output, sd.expected_output, sd.last_testcase, sd.runtime_error, sd.compile_error FROM submissions s INNER JOIN submission_details sd ON sd.submission_id = s.id WHERE s.title_slug = %s AND s.status_display != 'Accepted' ORDER BY s.submitted_at DESC LIMIT 4;", (title_slug, ))
    result = cursor.fetchall()

    cursor.close()
    conn.close()

    query = ""

    if len(result) == 0:
        query += "No past failed submissions found for this problem."
    for i in range(len(result)):
        sid, status, lang, submitted_at, code, codeop, exop, lasttc, runerr, comperr = result[i]
        if runerr is not None:
            query += f"""
            Attempt {i + 1} ({status}, {lang}):
            Code:
            {code}
            Runtime error: {runerr}
            """
        elif comperr is not None:
            query += f"""
            Attempt {i + 1} ({status}, {lang}):
            Code:
            {code}
            Compiler error: {comperr}
            """
        elif status == "Time Limit Exceeded":
            query += f"""
            Attempt {i + 1} ({status}, {lang}):
            Code:
            {code}
            Last Testcase: {lasttc}
            """
        else:
            query += f"""
            Attempt {i + 1} ({status}, {lang}):
            Code:
            {code}
            Code output: {codeop}
            Expected output: {exop}
            Last Testcase: {lasttc}
            """
    user_message = f"""
    Problem: {title_slug}

    Past failed attempts: 
    {query}

    Hints already given (do not repeat these):
    {chr(10).join(previous_hints) if previous_hints else "None yet, this is the first hint."}

    Generate hint level {level} now.
    """

    system_prompt = """
    You are a coding hint assistant. You will be given a user's PAST FAILED submissions 
    for a LeetCode problem (their code, error type, and failure details), plus any hints 
    already given to them for this problem in this session.

    Generate exactly ONE new hint, 2 to 5 lines long, for the requested level. Level 1 
    is the most subtle; higher levels get progressively more specific and direct.

    STRICT RULES:
    - NEVER reveal the specific test case, input values, or expected/actual output values, 
      even though they appear in the data you're given.
    - NEVER write or suggest corrected code, not even a partial snippet.
    - NEVER state the final fix directly, at any level — point at WHAT to reconsider and 
      WHY, not the literal corrected logic.
    - Phrase the hint in terms of the underlying concept or reasoning error (e.g. loop structure, 
      state updates, boundary handling, repeated work, ordering, invariants), so that the user must 
      reconstruct the implementation themselves rather than being reminded of how they previously coded it.
    - NEVER refer to, quote, or expose function names, variable names, class names, or other 
      implementation-specific identifiers from the past submission. Treat the old code only as 
      evidence for identifying the underlying reasoning/algorithmic mistake.
    - Do NOT repeat the substance of any previous hint listed below — this hint must add 
      genuinely new information.
    - Base your hint only on reasoning about the code's logic and structure.
    - Before writing the hint, carefully trace through the code's actual logic step by 
      step — loop ranges, conditions, and index bounds — rather than defaulting to 
      generic explanations (e.g. "redundant computation", "inefficiency") unless you can 
      verify them against what this specific code actually does.
    - If you identify a likely issue, double-check it by mentally tracing at least one 
      iteration of the relevant loop or condition before including it in the hint.
    - Output ONLY the hint text itself. No preamble, no "Here's a hint:", no markdown 
      formatting, no restating the level number.
    """

    response = client.chat.completions.create(
        model = "meta-llama/Llama-3.3-70B-Instruct",
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    )

    return response.choices[0].message.content