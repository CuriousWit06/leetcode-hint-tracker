# leetcode-hint-tracker


## A personal tool for revisiting solved LeetCode problems to aid revision

When placement season looms, you don't want to be spending time learning new patterns. Rather, you want to ensure that the ones you already know are solid. Most spaced repetition tools for LC track what you've solved and tell you when to revisit it, and that problem is solved (you can find plenty of extensions and CLI tools for that).

Now consider you pick up a problem that you solved 3 months ago, but you are not able to recall the approach you used back then. The fix? Either look up the solution (defeats the point of trying yourself), or just sit there taking shots in the dark.

This is where this tool steps in. When you get stuck on a revisit, it pulls up your own past submissions for a problem, and feeds that to an LLM (along with the code, the error you got, the TC that caused the error), to generate a personalised, leveled hint, giving you a direction to think in, by pointing "hey, this is where you fumbled last time".


### How it works

* **Data layer**: LeetCode has no official public API. Submission history (including your actual code) is accessible only through their internal GraphQL endpoint, authenticated via your session and csrf cookies. This tool reverse-engineers that endpoint to sync your full submission history, including all solved problems and their individual submission details, into a Postgres database.

* **Priority scoring**: All of the solved problems are ranked by a weighted formula, combining attempts-before-AC (measure of how much you struggled), difficulty tag of the question, and the days since you last attempted that question. Naturally, problems that you took more submissions to get an AC for, those that were tagged to be harder, and those that were last attempted long back rank higher.

* **Hint engine**: When you click "Get hint" on a problem, the tool fetches upto 4 of your most recent failed submissions for that problem from the database, formats the code and failure context, and sends it to an LLM with a carefully engineered prompt. Upto 4 hints are available for a problem, each escalating in specificity. Previous hints are passed with each new hint request so that the model never repeats itself.


### Tech Stack

* **Backend**: Python, FastAPI
* **Database**: PostgreSQL via Neon (serverless)
* **LLM**: Llama-3.3-70B-Instruct via Hugging Face Serverless Inference API


### Setup

```
git clone https://github.com/CuriousWit06/leetcode-hint-tracker
cd leetcode-hint-tracker
pip install -r requirements.txt
```

Create a ```.env``` file in the project root, containing: 
```
DATABASE_URL = your_neon_connection_string
HF_TOKEN = your_huggingface_token
LEETCODE_SESSION = your_leetcode_session_cookie
csrftoken = your_leetcode_csrf_token
```

* How to get your LeetCode cookies: 
Log in to https://leetcode.com, open DevTools -> Applications -> Cookies -> leetcode.com, and copy the values for ```LEETCODE_SESSION``` and ```csrftoken```.

* Start the server: 
```uvicorn api:app --reload```

Visit ```http://127.0.0.1:8000``` to open the dashboard.
On the first run, click on the ```sync``` button at the top right. Depending on how many problems you've solved, it may take upto 15 min to get your complete submission history. Subsequent syncs only process new problems and are, generally, faster.


### Known limitations

* **Hint accuracy on complex problems**: The LLM reasons about the code without executing it. Hints are reliably helpful on array, string, binary search, and similar lightweight problems. On dense multi-variable DP problems, however, the hints may be directionally correct but imprecise about the specific bug that your previous submission(s) encountered.

* **Cookie expiry**: LeetCode session cookies expire after a few days. When sync starts returning 0 problems (new problems are not getting synced), refresh the ```LEETCODE_SESSION``` and ```csrftoken``` values in ```.env``` from your browser, as described above.

* **Sync time**: Syncing takes several minutes due to rate limiting in LeetCode's API. The tool sleeps between requests to avoid trigerring blocks, and the sleep times, combined over hundreds of problems and multiple submissions for each, make the sync slow.


### What's next?

* Improvements in sync reliability and error handling.
* Improvements in hint accuracy on complex problems.