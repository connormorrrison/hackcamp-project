from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
import openai
import io
from PyPDF2 import PdfReader
import json
import logging

# Optional: enable CORS for local frontend (install flask-cors if you need it)
try:
    from flask_cors import CORS
    _HAS_CORS = True
except Exception:
    _HAS_CORS = False

load_dotenv()

# Basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4")  # change to gpt-3.5-turbo if needed

if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY
else:
    logger.warning("OPENAI_API_KEY not set. Please add it to your .env file.")

app = Flask(__name__)
if _HAS_CORS:
    CORS(app)  # allow all origins (OK for local dev)

@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "Backend running"}), 200

# Helper: extract visible text from a job posting URL (simple approach)
def extract_text_from_url(url, max_chars=4000):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; job-scraper/1.0)"}
        resp = requests.get(url, headers=headers, timeout=8)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Prefer <article> or <main> sections if present
        main = soup.find("article") or soup.find("main")
        if main:
            text = main.get_text(separator="\n", strip=True)
        else:
            paragraphs = soup.find_all("p")
            if paragraphs:
                text = "\n".join(p.get_text(strip=True) for p in paragraphs)
            else:
                body = soup.find("body")
                text = body.get_text(separator="\n", strip=True) if body else soup.get_text(separator="\n", strip=True)

        if len(text) > max_chars:
            text = text[:max_chars] + "\n... [truncated]"
        return text
    except Exception as e:
        logger.exception("Failed to fetch job posting URL")
        return f"[unable to fetch/extract job posting text: {str(e)}]"

# Helper: extract text from uploaded PDF (optional)
def extract_text_from_pdf_bytes(file_bytes, max_chars=8000):
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        texts = []
        for page in reader.pages:
            texts.append(page.extract_text() or "")
            if sum(len(t) for t in texts) > max_chars:
                break
        text = "\n".join(texts)
        if len(text) > max_chars:
            text = text[:max_chars] + "\n... [truncated]"
        return text
    except Exception as e:
        logger.exception("Failed to extract PDF text")
        return f"[unable to extract text from PDF: {str(e)}]"

@app.route("/generate", methods=["POST"])
def generate():
    if not OPENAI_API_KEY:
        return jsonify({"error": "OPENAI_API_KEY is not configured on the server."}), 500

    # Accept JSON or multipart/form-data (for optional file upload)
    resume_text = ""
    cover_letter = ""
    job_url = ""
    if request.content_type and "multipart/form-data" in request.content_type:
        resume_text = request.form.get("resume", "")
        cover_letter = request.form.get("coverLetter", "")
        job_url = request.form.get("jobUrl", "")
        pdf_file = request.files.get("resume_pdf")
        if pdf_file and not resume_text:
            resume_text = extract_text_from_pdf_bytes(pdf_file.read())
    else:
        data = request.get_json(force=True, silent=True) or {}
        resume_text = data.get("resume", "")
        cover_letter = data.get("coverLetter", "")
        job_url = data.get("jobUrl", "")

    model = (request.get_json(silent=True) or {}).get("model") or request.args.get("model") or MODEL

    if not (resume_text or cover_letter):
        return jsonify({"error": "Please provide at least resume text or a cover letter."}), 400

    job_posting_snippet = ""
    if job_url:
        job_posting_snippet = extract_text_from_url(job_url)

    system_prompt = (
        "You are an expert job-application assistant. "
        "Given a candidate's resume text, cover letter, and a job posting snippet, "
        "produce a JSON object only (no extra commentary) with the following keys:\n"
        " - optimized_resume: a concise, ATS-friendly resume tailored to the job, formatted in plain text with bullet points.\n"
        " - optimized_cover_letter: a short customized cover letter (3-6 short paragraphs) tailored to the job.\n"
        " - resume_suggestions: an array of short actionable suggestions to improve the resume (each item <= 2 sentences).\n"
        " - interview_questions: an array of 10 role-appropriate interview questions the candidate should prepare for.\n"
        " - hiring_manager_contact_info: an array of suggestions (each item: method, source, example search terms) describing how to find or attempt to contact the hiring manager or recruiter. Do NOT invent personal contact details; only provide methods and public sources.\n"
        "Keep each field concise. Return valid JSON parsable by a machine. If any input is missing, note that in a short field-specific message but still return a JSON structure.\n"
    )

    user_content = {
        "resume_text": resume_text,
        "cover_letter": cover_letter,
        "job_posting_snippet": job_posting_snippet,
        "job_url": job_url
    }

    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Here are the inputs (JSON):\n" + json.dumps(user_content, ensure_ascii=False)}
            ],
            temperature=0.2,
            max_tokens=1500
        )

        reply = response["choices"][0]["message"]["content"].strip()
        logger.debug("Raw model reply: %s", reply)

        try:
            parsed = json.loads(reply)
        except Exception:
            # Try to extract JSON substring if the model added commentary
            start = reply.find("{")
            end = reply.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    parsed = json.loads(reply[start:end+1])
                except Exception:
                    logger.exception("Failed to parse JSON from model reply")
                    return jsonify({"error": "Model output was not valid JSON", "raw_output": reply}), 500
            else:
                logger.error("Model output not JSON: %s", reply)
                return jsonify({"error": "Model output was not valid JSON", "raw_output": reply}), 500

        return jsonify({"result": parsed})
    except openai.error.OpenAIError as e:
        logger.exception("OpenAI API error")
        return jsonify({"error": "OpenAI API error", "details": str(e)}), 500
    except Exception as e:
        logger.exception("Unexpected error")
        return jsonify({"error": "Unexpected error", "details": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="127.0.0.1", port=port, debug=True)