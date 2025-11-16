from flask import Flask, request, jsonify
from latex_converter import convert_tex_to_pdf_direct
import tempfile
from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
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
    client = OpenAI(api_key = OPENAI_API_KEY)
else:
    client = OpenAI()
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
    job_description = ""
    if request.content_type and "multipart/form-data" in request.content_type:
        resume_text = request.form.get("resume", "")
        cover_letter = request.form.get("coverLetter", "")
        job_description = request.form.get("jobDescription", "")
        pdf_file = request.files.get("resume_pdf")
        if pdf_file and not resume_text:
            resume_text = extract_text_from_pdf_bytes(pdf_file.read())
    else:
        data = request.get_json(force=True, silent=True) or {}
        resume_text = data.get("resume", "")
        cover_letter = data.get("coverLetter", "")
        job_description = data.get("jobDescription", "")

    model = (request.get_json(silent=True) or {}).get("model") or request.args.get("model") or MODEL

    if not resume_text:
        return jsonify({"error": "Please provide a resume."}), 400

    if not job_description:
        return jsonify({"error": "Please provide a job description."}), 400

    system_prompt = (
        "You are an expert job-application assistant. "
        "Given a candidate's resume text and a job description, "
        "produce a JSON object only (no extra commentary) with the following keys:\n\n"

        "CRITICAL: DO NOT HALLUCINATE OR MAKE UP FALSE INFORMATION.\n"
        "- ONLY use information actually provided in the candidate's resume\n"
        "- DO NOT invent companies, positions, projects, or experiences\n"
        "- DO NOT fabricate achievements, metrics, or dates\n"
        "- DO NOT add fake contact information (use placeholder format if info missing)\n"
        "- You may reformat, reorganize, and enhance presentation of EXISTING information\n"
        "- You may tailor wording to match job description keywords from REAL experience\n"
        "- If resume lacks certain information, use generic placeholders (e.g., 'City, State', 'email@example.com')\n\n"

        "1. optimized_resume: A professional, ATS-friendly resume in LaTeX format. "
        "MUST include this COMPLETE preamble with all custom command definitions:\n\n"
        "\\DocumentMetadata{}\n"
        "\\documentclass[letterpaper,11pt]{article}\n"
        "\\usepackage{latexsym}\n"
        "\\usepackage[empty]{fullpage}\n"
        "\\usepackage{titlesec}\n"
        "\\usepackage{marvosym}\n"
        "\\usepackage[usenames,dvipsnames]{color}\n"
        "\\usepackage{verbatim}\n"
        "\\usepackage{enumitem}\n"
        "\\usepackage[hidelinks]{hyperref}\n"
        "\\usepackage{fancyhdr}\n"
        "\\usepackage{tabularx}\n"
        "\\pagestyle{fancy}\n"
        "\\fancyhf{}\n"
        "\\renewcommand{\\headrulewidth}{0pt}\n"
        "\\addtolength{\\oddsidemargin}{-0.5in}\n"
        "\\addtolength{\\evensidemargin}{-0.5in}\n"
        "\\addtolength{\\textwidth}{1in}\n"
        "\\addtolength{\\topmargin}{-.5in}\n"
        "\\addtolength{\\textheight}{1.0in}\n"
        "\\urlstyle{same}\n"
        "\\raggedbottom\n"
        "\\raggedright\n"
        "\\setlength{\\tabcolsep}{0in}\n"
        "\\titleformat{\\section}{\\vspace{-4pt}\\scshape\\raggedright\\large}{}{0em}{}[\\color{black}\\titlerule \\vspace{-5pt}]\n"
        "\\newcommand{\\resumeItem}[1]{\\item\\small{{#1 \\vspace{-2pt}}}}\n"
        "\\newcommand{\\resumeSubheading}[4]{\\vspace{-2pt}\\item\\begin{tabular*}{0.97\\textwidth}[t]{l@{\\extracolsep{\\fill}}r}\\textbf{#1} & #2 \\\\\\textit{\\small#3} & \\textit{\\small #4} \\\\\\end{tabular*}\\vspace{-7pt}}\n"
        "\\newcommand{\\resumeProjectHeading}[2]{\\item\\begin{tabular*}{0.97\\textwidth}{l@{\\extracolsep{\\fill}}r}\\small#1 & #2 \\\\\\end{tabular*}\\vspace{-7pt}}\n"
        "\\newcommand{\\resumeSubHeadingListStart}{\\begin{itemize}[leftmargin=0.15in, label={}]}\n"
        "\\newcommand{\\resumeSubHeadingListEnd}{\\end{itemize}}\n"
        "\\newcommand{\\resumeItemListStart}{\\begin{itemize}}\n"
        "\\newcommand{\\resumeItemListEnd}{\\end{itemize}\\vspace{-5pt}}\n\n"

        "Then include content sections:\n"
        "- HEADING: \\begin{center}\\textbf{\\Huge \\scshape Name} with contact info (phone, email, LinkedIn, GitHub)\\end{center}\n\n"

        "- EDUCATION: \\section{Education}\\resumeSubHeadingListStart\\resumeSubheading{School}{Dates}{Degree}{Location}\\resumeSubHeadingListEnd\n"
        "  * Include GPA if 3.5+, relevant coursework, honors, or awards\n\n"

        "- EXPERIENCE: \\section{Experience}\\resumeSubHeadingListStart\n"
        "  * For EACH position: \\resumeSubheading{Position}{Dates}{Company}{Location}\\resumeItemListStart\n"
        "  * Include 4-6 bullet points per position using \\resumeItem{}\n"
        "  * Start each bullet with strong action verbs (Developed, Built, Led, Designed, Implemented, Optimized, etc.)\n"
        "  * QUANTIFY achievements with metrics (increased by X%, reduced by Y hours, processed Z requests, etc.)\n"
        "  * Highlight technologies/tools used that match job description\n"
        "  * Show impact and results, not just responsibilities\n"
        "  * Even if limited info provided, infer realistic technical achievements based on role\n"
        "  * \\resumeItemListEnd\\resumeSubHeadingListEnd\n\n"

        "- PROJECTS: \\section{Projects}\\resumeSubHeadingListStart\n"
        "  * Include 2-3 relevant projects if applicable\n"
        "  * Format: \\resumeProjectHeading{\\textbf{Project Name} $|$ \\emph{Tech Stack}}{Date}\\resumeItemListStart\n"
        "  * 2-3 bullet points per project describing features, impact, and technologies\n"
        "  * \\resumeItemListEnd\\resumeSubHeadingListEnd\n\n"

        "- TECHNICAL SKILLS: \\section{Technical Skills}\\begin{itemize}[leftmargin=0.15in, label={}]\\small{\\item{\n"
        "  \\textbf{Languages}{: List all programming languages} \\\\\n"
        "  \\textbf{Frameworks}{: List frameworks and libraries} \\\\\n"
        "  \\textbf{Developer Tools}{: Git, Docker, CI/CD, cloud platforms, etc.} \\\\\n"
        "  \\textbf{Libraries}{: Relevant libraries}\n"
        "  }}\\end{itemize}\n\n"

        "- OPTIONAL SECTIONS (add if relevant):\n"
        "  * Certifications: AWS, Google Cloud, etc.\n"
        "  * Leadership/Activities: clubs, volunteer work\n"
        "  * Publications/Research: if applicable\n\n"

        "- End with \\end{document}\n\n"

        "IMPORTANT GUIDELINES:\n"
        "- Tailor content to match job description keywords using ACTUAL experience from resume\n"
        "- Use strong action verbs and quantify achievements (only if data exists in resume)\n"
        "- Reformat and reorganize existing information for better presentation\n"
        "- Highlight transferable skills and relevant technologies mentioned in resume\n"
        "- DO NOT add experience, skills, or details not present in original resume\n"
        "- Properly escape LaTeX special chars (\\&, \\%, \\$, \\#, \\_)\n\n"

        "2. optimized_cover_letter: Professional cover letter in simple LaTeX article format. "
        "MUST include this COMPLETE structure:\n\n"
        "\\DocumentMetadata{}\n"
        "\\documentclass[11pt,letterpaper]{article}\n"
        "\\usepackage[margin=1in]{geometry}\n"
        "\\usepackage{parskip}\n"
        "\\begin{document}\n"
        "\\pagestyle{empty}\n\n"
        "\\begin{flushleft}\n"
        "First Last\\\\\\\\\n"
        "Phone\\\\\\\\\n"
        "Email\n"
        "\\end{flushleft}\n\n"
        "\\vspace{0.5cm}\n\n"
        "\\today\n\n"
        "\\vspace{0.5cm}\n\n"
        "Hiring Manager\\\\\\\\\n"
        "Company Name\n\n"
        "\\vspace{0.5cm}\n\n"
        "Dear Hiring Manager,\n\n"
        "3-4 paragraphs highlighting ACTUAL experience from resume tailored to job description.\n"
        "DO NOT fabricate experience or make false claims.\n"
        "Only reference real skills and achievements from the provided resume.\n\n"
        "Sincerely,\n\n"
        "First Last\n\n"
        "\\end{document}\n\n"

        "3. resume_suggestions: Array of 3-5 actionable suggestions (each <= 2 sentences)\n\n"

        "Return ONLY valid JSON.\n"
    )

    user_content = {
        "resume_text": resume_text,
        "cover_letter": cover_letter,
        "job_description": job_description
    }

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Here are the inputs (JSON):\n" + json.dumps(user_content, ensure_ascii=False)}
            ],
            temperature=0.2,
        )

        reply = response.choices[0].message.content.strip()
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
    except Exception as e:
        logger.exception("Error in generate endpoint")
        return jsonify({"error": "Error processing request", "details": str(e)}), 500
#Convert LaTex into pdf
@app.route("/convert-latex-to-pdf", methods=["POST"])
def convert_latex_to_pdf():
    #Accepts LaTex resume textand return pdf bytes. Expectes JSON: {"latex_content": "<LaTex code>"}
    data = request.get_json(force=True, silent=True) or {}
    latex_content = data.get("latex_content", "").strip()

    if not latex_content:
        return jsonify({"error": "Please provide latex_content in the request body."})

    # Log the first 500 chars of LaTeX for debugging
    logger.info(f"Received LaTeX content (first 500 chars):\n{latex_content[:500]}")

    # FIX: Escape unescaped ampersands in document content (not in preamble command definitions)
    # Only escape & that appear after \begin{document}
    import re
    if '\\begin{document}' in latex_content:
        parts = latex_content.split('\\begin{document}', 1)
        preamble = parts[0]
        content = parts[1] if len(parts) > 1 else ''

        # Count unescaped ampersands in content only
        unescaped_count = len(re.findall(r'(?<!\\)&', content))

        # Escape & in content only (not in preamble where they're used for tabular column separators)
        content = re.sub(r'(?<!\\)&', r'\\&', content)

        latex_content = preamble + '\\begin{document}' + content

        if unescaped_count > 0:
            logger.info(f"Escaped {unescaped_count} unescaped ampersands in document content")

    # FIX: Ensure DocumentMetadata is present for TeX Live 2024+ compatibility
    # This prevents "Forbidden control sequence" errors with the new tagging system
    if '\\DocumentMetadata' not in latex_content:
        # Check if it starts with \documentclass
        if latex_content.strip().startswith('\\documentclass'):
            logger.info("Adding \\DocumentMetadata{} to LaTeX content for TeX Live 2024+ compatibility")
            latex_content = '\\DocumentMetadata{}\n' + latex_content
        else:
            # Find the \documentclass line and insert before it
            lines = latex_content.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith('\\documentclass'):
                    logger.info(f"Inserting \\DocumentMetadata{{}} before \\documentclass at line {i}")
                    lines.insert(i, '\\DocumentMetadata{}')
                    latex_content = '\n'.join(lines)
                    break

    # Additional fix: Disable tagging in tabular environments to prevent errors
    # Find \begin{document} and insert the fix right after it
    if '\\begin{document}' in latex_content and 'tagpdfparaOff' not in latex_content:
        logger.info("Adding tabular tagging fix for TeX Live 2024+ compatibility")
        tagging_fix = r'''
% Fix for TeX Live 2024+ tagging system in tabular environments
\makeatletter
\@ifundefined{tagpdfparaOff}{}{
  \AddToHook{env/tabular*/begin}{\tagpdfparaOff}
  \AddToHook{env/tabular*/end}{\tagpdfparaOn}
  \AddToHook{env/tabular/begin}{\tagpdfparaOff}
  \AddToHook{env/tabular/end}{\tagpdfparaOn}
}
\makeatother
'''
        latex_content = latex_content.replace('\\begin{document}', tagging_fix + '\n\\begin{document}')

    temp_tex_path = None
    try:
        # Save debug copy of LaTeX (for troubleshooting)
        debug_path = os.path.join(os.path.dirname(__file__), 'last_generated.tex')
        try:
            with open(debug_path, 'w') as f:
                f.write(latex_content)
            logger.info(f"Saved debug LaTeX to {debug_path}")
        except Exception as e:
            logger.warning(f"Could not save debug LaTeX: {e}")

        # Write LaTeX to a temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as tf:
            tf.write(latex_content)
            temp_tex_path = tf.name

        # Convert to PDF
        # The new professional template is self-contained (doesn't need .cls file)
        # But we keep the cls_path for backwards compatibility
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        cls_path = os.path.join(backend_dir, 'LaTex', 'resume.cls')

        # Only use cls file if it exists and LaTeX references it
        if '\\documentclass{resume}' in latex_content and os.path.exists(cls_path):
            pdf_bytes = convert_tex_to_pdf_direct(temp_tex_path, cls_path)
        else:
            pdf_bytes = convert_tex_to_pdf_direct(temp_tex_path, None)

        # Return PDF as binary response
        return pdf_bytes, 200, {
            'Content-Type': 'application/pdf',
            'Content-Disposition': 'attachment; filename="document.pdf"'
        }
    except FileNotFoundError as e:
        logger.exception("File not found during LaTeX conversion")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.exception("Failed to convert LaTeX to PDF")
        return jsonify({"error": "LaTeX to PDF conversion failed", "details": str(e)}), 500
    finally:
        # Clean up temp file
        if temp_tex_path and os.path.exists(temp_tex_path):
            try:
                os.unlink(temp_tex_path)
            except:
                pass
    
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="127.0.0.1", port=port, debug=True)