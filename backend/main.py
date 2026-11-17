import os
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.analyzer.text_extractor import extract_text
from backend.analyzer.ats_engine import ATSEngine
from backend.analyzer.ai_service import AIService

app = FastAPI(title="AI Resume & ATS Analyzer API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ats_engine = ATSEngine()
ai_service = AIService()

class BulletRewriteRequest(BaseModel):
    bullet: str
    jd_text: Optional[str] = ""
    target_skill: Optional[str] = ""
    api_key: Optional[str] = None

class CoverLetterRequest(BaseModel):
    resume_text: str
    jd_text: Optional[str] = ""
    candidate_name: Optional[str] = ""
    company_name: Optional[str] = ""
    role_title: Optional[str] = ""
    api_key: Optional[str] = None

class InterviewPrepRequest(BaseModel):
    resume_text: str
    jd_text: Optional[str] = ""
    skills_data: Optional[dict] = None
    api_key: Optional[str] = None

@app.post("/api/extract-file")
def extract_file_endpoint(file: UploadFile = File(...)):
    """Extracts text from an uploaded resume file and returns preview & metadata."""
    try:
        if hasattr(file, 'file') and hasattr(file.file, 'read'):
            file_bytes = file.file.read()
        else:
            file_bytes = file.read()
        text, metadata = extract_text(file_bytes, file.filename or "resume.pdf")
        return {
            "success": True,
            "filename": file.filename,
            "text": text,
            "char_count": len(text),
            "metadata": metadata
        }
    except Exception as e:
        return JSONResponse(status_code=400, content={"success": False, "detail": str(e)})

@app.post("/api/analyze")
def analyze_resume(
    file: Optional[UploadFile] = File(None),
    resume_text: Optional[str] = Form(None),
    jd_text: Optional[str] = Form(""),
    api_key: Optional[str] = Form(None)
):
    try:
        final_resume_text = ""
        metadata = {}

        if file and file.filename:
            if hasattr(file, 'file') and hasattr(file.file, 'read'):
                file_bytes = file.file.read()
            else:
                file_bytes = file.read()
            final_resume_text, metadata = extract_text(file_bytes, file.filename)
        elif resume_text and resume_text.strip():
            final_resume_text = resume_text.strip()
            metadata = {"format": "text", "char_count": len(final_resume_text), "is_scanned_or_empty": len(final_resume_text) < 30}
        else:
            raise HTTPException(status_code=400, detail="Please upload a resume file (PDF, DOCX, TXT) or paste resume text.")

        if metadata.get("is_scanned_or_empty"):
            raise HTTPException(
                status_code=400,
                detail="Resume text could not be extracted or file is empty. If using an image/scanned PDF, please use a text-based PDF or paste text directly."
            )

        clean_jd = (jd_text or "").strip()

        # 1. Run ATS Scoring Engine (supports both targeted JD and standalone general ATS audit)
        ats_results = ats_engine.analyze(final_resume_text, clean_jd)

        # 2. Run AI Recruiter Review
        ai_review = ai_service.generate_deep_review(
            resume_text=final_resume_text,
            jd_text=clean_jd,
            ats_data=ats_results,
            api_key=api_key
        )

        return JSONResponse(content={
            "success": True,
            "metadata": metadata,
            "has_target_job": bool(clean_jd and len(clean_jd) >= 20),
            "resume_text_sample": final_resume_text[:400] + "..." if len(final_resume_text) > 400 else final_resume_text,
            "full_resume_text": final_resume_text,
            "ats_results": ats_results,
            "ai_review": ai_review
        })
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "detail": str(e)})

@app.post("/api/ai/rewrite-bullet")
def rewrite_bullet(req: BulletRewriteRequest):
    if not req.bullet.strip():
        raise HTTPException(status_code=400, detail="Bullet point text is required.")
    result = ai_service.rewrite_bullet(
        bullet=req.bullet,
        jd_text=req.jd_text or "",
        target_skill=req.target_skill or "",
        api_key=req.api_key
    )
    return {"success": True, "variations": result}

@app.post("/api/ai/cover-letter")
def generate_cover_letter(req: CoverLetterRequest):
    if not req.resume_text.strip():
        raise HTTPException(status_code=400, detail="Resume text is required.")
    letter = ai_service.generate_cover_letter(
        resume_text=req.resume_text,
        jd_text=req.jd_text or "",
        candidate_name=req.candidate_name or "",
        company_name=req.company_name or "",
        role_title=req.role_title or "",
        api_key=req.api_key
    )
    return {"success": True, "cover_letter": letter}

@app.post("/api/ai/interview-prep")
def generate_interview_prep(req: InterviewPrepRequest):
    if not req.resume_text.strip():
        raise HTTPException(status_code=400, detail="Resume text is required.")
    questions = ai_service.generate_interview_prep(
        resume_text=req.resume_text,
        jd_text=req.jd_text or "",
        skills_data=req.skills_data or {},
        api_key=req.api_key
    )
    return {"success": True, "questions": questions}

@app.get("/api/sample-data/{sample_type}")
def get_sample_data(sample_type: str):
    prefix = "swe" if sample_type == "swe" else "ds"
    resume_path = os.path.join("samples", f"sample_resume_{prefix}.txt")
    jd_path = os.path.join("samples", f"sample_jd_{prefix}.txt")

    if not os.path.exists(resume_path) or not os.path.exists(jd_path):
        raise HTTPException(status_code=404, detail="Sample not found")

    with open(resume_path, "r", encoding="utf-8") as f:
        resume_content = f.read()
    with open(jd_path, "r", encoding="utf-8") as f:
        jd_content = f.read()

    return {
        "sample_type": sample_type,
        "resume": resume_content,
        "job_description": jd_content
    }

static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def serve_index():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "AI Resume & ATS Analyzer API is online. Place index.html in backend/static."}
