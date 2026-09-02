# AI Job Match Assistant

A beginner-friendly web application designed to help job seekers evaluate how well their resume matches a specific job description. Powered by Google Gemini and Flask, the application extracts text from PDF resumes, calculates structured match scores, identifies skill gaps, offers section-by-section resume improvements, and generates clear, beginner-friendly match explanations without inventing credentials.

---

## Features

- **PDF Resume Text Extraction**: Upload resume documents directly in PDF format (`.pdf`) using PyPDF2 with editable text output.
- **AI-Powered Match Analysis**: Evaluates resume content against job descriptions using strict, grounded instructions to prevent hallucinated skills or experiences.
- **Structured Scoring & Breakdown**:
  - Overall Match Score (0–100%)
  - Matching Skills & Missing Skills tags
  - Experience Match summary
  - Identified Gaps & Actionable Recommendations
- **Resume Improvement Coach (`IMPROVE MY RESUME`)**: Generates targeted wording and presentation suggestions organized by resume sections based on identified gaps.
- **Match Explainer (`EXPLAIN MY MATCH`)**: Provides plain-language explanations of why the candidate received their match score and what to focus on next.
- **Strict Pydantic Validation**: Guarantees typed, reliable structured outputs directly from the Gemini API.

---

## Tech Stack

- **Backend**: Python, Flask
- **AI & SDK**: Google GenAI SDK (`google-genai`), Google Gemini Models
- **Data Validation**: Pydantic v2
- **PDF Processing**: PyPDF2
- **Environment Management**: python-dotenv
- **Frontend**: Vanilla HTML5, CSS3, JavaScript (Fetch API)

---

## Project Structure

```
ai-job-match/
├── .env                  # Environment variables (API keys, Flask config)
├── .gitignore            # Git ignore patterns for virtual environments and secrets
├── requirements.txt      # Python dependencies
├── app.py                # Flask application routes, Gemini integration & validation
├── templates/
│   └── index.html        # Single-page web interface with responsive styling
└── README.md             # Project documentation
```

---

## Setup & Configuration

### 1. Prerequisites
- Python 3.10+ installed
- A Google Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

### 2. Installation
Clone or navigate to the project directory and install required packages:

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Create or edit the `.env` file in the root directory:

```env
FLASK_APP=app.py
FLASK_ENV=development
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

---

## How to Run

Start the Flask development server:

```bash
python app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000/
```

---

## How to Use

1. **Add Your Resume**:
   - Paste resume text directly into the **Resume** textarea, OR
   - Click **Choose File** / **Upload PDF** to extract text from a `.pdf` file.
2. **Add Job Description**:
   - Paste the target job posting into the **Job Description** textarea.
3. **Analyze**:
   - Click **Analyze Match** to generate the Match Report.
4. **Take Action**:
   - Click **IMPROVE MY RESUME** for tailored suggestions to enhance specific sections.
   - Click **EXPLAIN MY MATCH** for an easy-to-understand breakdown of your score.

---

## API Endpoints

### 1. `GET /`
- **Description**: Renders the web interface.
- **Response**: HTML page.

### 2. `GET /api/test`
- **Description**: Verifies Gemini API connectivity.
- **Response**:
  ```json
  {
    "success": true,
    "message": "Gemini API connection working"
  }
  ```

### 3. `POST /api/extract-resume`
- **Description**: Extracts raw text from an uploaded PDF file.
- **Content-Type**: `multipart/form-data`
- **Payload**: `resume_pdf` (file, `.pdf`)
- **Response**:
  ```json
  {
    "success": true,
    "resume_text": "Extracted text content..."
  }
  ```

### 4. `POST /api/analyze`
- **Description**: Evaluates resume against job description using Gemini structured output.
- **Payload**:
  ```json
  {
    "resume": "Candidate resume text...",
    "job_description": "Job description text..."
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "match_score": 85,
    "matching_skills": ["Python", "Flask"],
    "missing_skills": ["Docker"],
    "experience_match": "Candidate meets the experience requirements...",
    "gaps": ["No containerization experience listed"],
    "recommendations": ["Learn Docker basics and containerize a project"]
  }
  ```

### 5. `POST /api/improve-resume`
- **Description**: Recommends targeted phrasing and section improvements based on analysis gaps.
- **Payload**:
  ```json
  {
    "resume": "Candidate resume text...",
    "gaps": ["Missing Docker experience"],
    "recommendations": ["Learn Docker basics"]
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "improved_sections": [
      {
        "section": "Skills",
        "suggestion": "Add containerization tools once foundational knowledge is acquired."
      }
    ]
  }
  ```

### 6. `POST /api/explain-match`
- **Description**: Generates a beginner-friendly explanation of the match score without recalculating.
- **Payload**:
  ```json
  {
    "resume": "Candidate resume text...",
    "job_description": "Job description text...",
    "analysis": {
      "match_score": 85,
      "matching_skills": ["Python", "Flask"],
      "missing_skills": ["Docker"],
      "experience_match": "...",
      "gaps": ["..."],
      "recommendations": ["..."]
    }
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "explanation": "You received an 85/100 score because your core Python and Flask skills match well..."
  }
  ```

---

## Security Note

- **API Keys**: Never commit your `.env` file or hardcode your `GEMINI_API_KEY` into source control.
- **Git Ignore**: The included `.gitignore` ensures `.env` and virtual environment files (`.venv/`, `venv/`) remain excluded from version control.
- **Prompt Grounding**: Prompts strictly instruct the model to evaluate only explicitly stated facts to mitigate hallucinated credentials or biased assumptions.

---

## Future Improvements

- **Export Reports**: Download analysis reports and improvement suggestions as PDF or Markdown.
- **Multiple Resume Comparison**: Compare multiple resumes against a single job description.
- **DOCX / TXT Support**: Expand document extraction to support Microsoft Word (`.docx`) files.
- **Job Keyword Highlighter**: Visually highlight matching and missing keywords within the resume text editor.
