import io
import json
import os
from typing import List
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
import PyPDF2

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)

# Structured Output Schema
class JobMatchAnalysis(BaseModel):
    match_score: int = Field(ge=0, le=100, description="Match score from 0 to 100")
    matching_skills: List[str] = Field(default_factory=list, description="Array of matching skill strings")
    missing_skills: List[str] = Field(default_factory=list, description="Array of missing skill strings")
    experience_match: str = Field(default="", description="Short string describing experience match")
    gaps: List[str] = Field(default_factory=list, description="Array of identified gaps")
    recommendations: List[str] = Field(default_factory=list, description="Array of practical recommendations")

# Initialize Gemini Client using API key from .env
gemini_api_key = os.getenv("GEMINI_API_KEY")
try:
    client = genai.Client(api_key=gemini_api_key) if gemini_api_key else None
except Exception:
    client = None

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/api/test', methods=['GET'])
def test_gemini():
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return jsonify({
                "success": False,
                "message": "Gemini API connection failed"
            })

        gemini_client = client or genai.Client(api_key=api_key)
        response = gemini_client.models.generate_content(
            model="gemini-3.6-flash",
            contents="ping"
        )
        if response and response.text:
            return jsonify({
                "success": True,
                "message": "Gemini API connection working"
            })
        return jsonify({
            "success": False,
            "message": "Gemini API connection failed"
        })
    except Exception:
        return jsonify({
            "success": False,
            "message": "Gemini API connection failed"
        })

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Invalid JSON"
        }), 400

    resume = data.get("resume")
    job_description = data.get("job_description")

    if not resume or not isinstance(resume, str) or not resume.strip():
        return jsonify({
            "success": False,
            "message": "Resume is required"
        }), 400

    if not job_description or not isinstance(job_description, str) or not job_description.strip():
        return jsonify({
            "success": False,
            "message": "Job description is required"
        }), 400

    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return jsonify({
                "success": False,
                "message": "AI response validation failed"
            }), 502

        gemini_client = client or genai.Client(api_key=api_key)

        prompt_text = (
            "You are an AI job matching assistant.\n"
            "compare this candidate's resume against the supplied job description\n\n"
            "Evaluate ONLY information explicitly present in the supplied resume and job desription \n\n"
            "Do not invent:\n"
            "-skills\n"
            "-work experience\n"
            "-education\n"
            "-certifications\n"
            "-projects\n\n"
            "Return a match analyse containing:\n"
            "- match_score: integer from 0 to 100\n"
            "- matching_skills: array of strings\n"
            "- missing_skills: array of strings\n"
            "- experience_match:short string\n"
            "- gaps:array of strings\n"
            "-recomendations: array of strings\n\n"
            "the recomendations must be practical and based only on the identified gaps.\n\n"
            f"Candidate Resume:\n{resume.strip()}\n\n"
            f"Job Description:\n{job_description.strip()}"
        )

        response = gemini_client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt_text,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=JobMatchAnalysis
            )
        )

        if not response or not response.text:
            return jsonify({
                "success": False,
                "message": "AI response validation failed"
            }), 502

        # Validate with Pydantic
        validated_data = JobMatchAnalysis.model_validate_json(response.text)

        return jsonify({
            "success": True,
            "match_score": validated_data.match_score,
            "matching_skills": validated_data.matching_skills,
            "missing_skills": validated_data.missing_skills,
            "experience_match": validated_data.experience_match,
            "gaps": validated_data.gaps,
            "recommendations": validated_data.recommendations
        })

    except Exception:
        return jsonify({
            "success": False,
            "message": "AI response validation failed"
        }), 502
# Structured Output Schema for resume improvement
class ResumeImprovementSection(BaseModel):
    section: str = Field(description="Name of the resume section to improve")
    suggestion: str = Field(description="Specific, actionable suggestion for that section")

class ResumeImprovementResponse(BaseModel):
    improved_sections: List[ResumeImprovementSection] = Field(
        default_factory=list,
        description="List of section-level improvement suggestions"
    )

@app.route('/api/improve-resume', methods=['POST'])
def improve_resume():
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Invalid JSON"
        }), 400

    resume = data.get("resume")
    gaps = data.get("gaps") or []
    recommendations = data.get("recommendations") or []

    if not resume or not isinstance(resume, str) or not resume.strip():
        return jsonify({
            "success": False,
            "message": "Resume is required"
        }), 400

    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return jsonify({
                "success": False,
                "message": "Resume improvement failed"
            }), 502

        gemini_client = client or genai.Client(api_key=api_key)

        gaps_text = "\n".join(f"- {g}" for g in gaps) if gaps else "None provided."
        recs_text = "\n".join(f"- {r}" for r in recommendations) if recommendations else "None provided."

        prompt_text = (
            "You are a professional resume coach.\n"
            "Your task is to suggest targeted improvements to the candidate's existing resume "
            "based ONLY on the identified gaps and recommendations provided below.\n\n"
            "CRITICAL RULES — you must NEVER:\n"
            "- Invent new work experience\n"
            "- Invent new projects\n"
            "- Invent new skills\n"
            "- Invent new certifications\n"
            "- Invent new education\n"
            "- Invent new achievements\n\n"
            "You MAY:\n"
            "- Improve the wording or clarity of existing content\n"
            "- Suggest how existing experience could be presented more effectively\n"
            "- Suggest what the candidate should learn or add to their resume in the future\n\n"
            "For each suggestion, identify the specific resume section it applies to "
            "(e.g. 'Skills', 'Work Experience', 'Summary', 'Projects').\n\n"
            f"Candidate Resume:\n{resume.strip()}\n\n"
            f"Identified Gaps:\n{gaps_text}\n\n"
            f"Recommendations:\n{recs_text}"
        )

        response = gemini_client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt_text,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ResumeImprovementResponse
            )
        )

        if not response or not response.text:
            return jsonify({
                "success": False,
                "message": "Resume improvement failed"
            }), 502

        validated = ResumeImprovementResponse.model_validate_json(response.text)

        return jsonify({
            "success": True,
            "improved_sections": [
                {"section": s.section, "suggestion": s.suggestion}
                for s in validated.improved_sections
            ]
        })

    except Exception:
        return jsonify({
            "success": False,
            "message": "Resume improvement failed"
        }), 502

@app.route('/api/explain-match', methods=['POST'])
def explain_match():
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Invalid JSON"
        }), 400

    resume = data.get("resume")
    job_description = data.get("job_description")
    analysis = data.get("analysis")

    if not resume or not isinstance(resume, str) or not resume.strip():
        return jsonify({
            "success": False,
            "message": "Resume is required"
        }), 400

    if not job_description or not isinstance(job_description, str) or not job_description.strip():
        return jsonify({
            "success": False,
            "message": "Job description is required"
        }), 400

    if not analysis or not isinstance(analysis, dict):
        return jsonify({
            "success": False,
            "message": "Analysis object is required"
        }), 400

    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return jsonify({
                "success": False,
                "message": "Match explanation failed"
            }), 502

        gemini_client = client or genai.Client(api_key=api_key)

        match_score = analysis.get("match_score", "N/A")
        matching_skills = analysis.get("matching_skills") or []
        missing_skills = analysis.get("missing_skills") or []
        experience_match = analysis.get("experience_match", "")
        gaps = analysis.get("gaps") or []
        recommendations = analysis.get("recommendations") or analysis.get("recomendations") or []

        matching_skills_text = ", ".join(matching_skills) if matching_skills else "None"
        missing_skills_text = ", ".join(missing_skills) if missing_skills else "None"
        gaps_text = "\n".join(f"- {g}" for g in gaps) if gaps else "None"
        recs_text = "\n".join(f"- {r}" for r in recommendations) if recommendations else "None"

        prompt_text = (
            "You are a friendly career advisor explaining a job match result to a student or junior candidate.\n\n"
            "IMPORTANT RULES:\n"
            "- Base your explanation ONLY on the resume, job description, and analysis provided below.\n"
            "- Do NOT recalculate or change the match score.\n"
            "- Do NOT invent any information not present in the resume or job description.\n\n"
            "Write a clear, beginner-friendly paragraph (3-5 sentences) that:\n"
            "1. States the match score and what it generally means\n"
            "2. Highlights the strongest matching skills or experience\n"
            "3. Explains the most important gaps or missing skills\n"
            "4. Tells the candidate what they could focus on to improve\n\n"
            "Return ONLY the explanation as a plain text string. No JSON, no headings, no bullet points.\n\n"
            f"Match Score: {match_score}/100\n"
            f"Matching Skills: {matching_skills_text}\n"
            f"Missing Skills: {missing_skills_text}\n"
            f"Experience Match: {experience_match}\n"
            f"Gaps:\n{gaps_text}\n"
            f"Recommendations:\n{recs_text}\n\n"
            f"Candidate Resume:\n{resume.strip()}\n\n"
            f"Job Description:\n{job_description.strip()}"
        )

        response = gemini_client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt_text
        )

        if not response or not response.text or not response.text.strip():
            return jsonify({
                "success": False,
                "message": "Match explanation failed"
            }), 502

        return jsonify({
            "success": True,
            "explanation": response.text.strip()
        })

    except Exception:
        return jsonify({
            "success": False,
            "message": "Match explanation failed"
        }), 502

@app.route('/api/extract-resume', methods=['POST'])
def extract_resume():
    # Verify a file was provided
    if 'resume_pdf' not in request.files:
        return jsonify({
            "success": False,
            "message": "Resume PDF is required"
        }), 400

    file = request.files['resume_pdf']

    # Verify a filename is present (empty file field)
    if not file or file.filename == '':
        return jsonify({
            "success": False,
            "message": "Resume PDF is required"
        }), 400

    # Verify it is a PDF file
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({
            "success": False,
            "message": "Only PDF files are allowed"
        }), 400

    # Extract text from the PDF
    try:
        pdf_bytes = file.read()
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))

        extracted_pages = []
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                extracted_pages.append(page_text)

        resume_text = "\n".join(extracted_pages).strip()

        if not resume_text:
            return jsonify({
                "success": False,
                "message": "Could not extract text from PDF"
            }), 400

        return jsonify({
            "success": True,
            "resume_text": resume_text
        })

    except Exception:
        return jsonify({
            "success": False,
            "message": "Could not extract text from PDF"
        }), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)






