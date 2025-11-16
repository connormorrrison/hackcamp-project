from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json

    resume = data.get("resume", "")
    cover_letter = data.get("coverLetter", "")
    job_url = data.get("jobUrl", "")

    response = client.responses.create(
        model="gpt-5.1",
        input=[
            {
                "role": "system",
                "content": (
                    "You are an expert job application assistant. "
                    "Generate optimized resume, cover letter, resume suggestions, "
                    "interview questions, and hiring manager contact steps. "
                    "Return ONLY valid JSON."
                )
            },
            {
                "role": "user",
                "content": {
                    "resume": resume,
                    "cover_letter": cover_letter,
                    "job_posting_url": job_url
                }
            }
        ],
        url=job_url
    )

    return jsonify({"result": response.output_text})

if __name__ == "__main__":
    app.run(debug=True)
