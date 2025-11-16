import os
import PyPDF2
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

model = "gpt-5-mini-2025-08-07"
temperature = "0.7"
