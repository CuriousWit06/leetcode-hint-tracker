from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    base_url = "https://router.huggingface.co/v1",
    api_key = os.environ.get("HF_TOKEN")
)

response = client.chat.completions.create(
    model = "meta-llama/Llama-3.3-70B-Instruct",
    messages = [
        {"role": "user", "content": "How are you doing?"}
    ]
)
print(response.choices[0].message.content)