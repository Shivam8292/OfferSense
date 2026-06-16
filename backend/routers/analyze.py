from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from pydantic import BaseModel
from services.pdf_extractor import extract_offer_details
from services.salary_fetcher import fetch_salary_data
from services.ai_analyzer import analyze_offer
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(prefix="/analyze", tags=["analyze"])
limiter = Limiter(key_func=get_remote_address)

class ManualInput(BaseModel):
    role: str
    company: str
    city: str
    ctc_lpa: float
    experience_years: int = 0

def build_response(extracted: dict, market: dict, analysis: dict) -> dict:
    return {
        "extracted": extracted,
        "market": market,
        "verdict": analysis["verdict"],
        "counter_offer": analysis["counter_offer"],
        "script": analysis["script"]
    }

@router.post("/pdf")
@limiter.limit("10/minute")
async def analyze_pdf(request: Request, file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files accepted")
    
    # Check file size (max 10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    pdf_bytes = await file.read()
    if len(pdf_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum size allowed is 10MB.")
    
    try:
        extracted = extract_offer_details(pdf_bytes)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not extract offer details: {str(e)}")
    
    if not extracted.get("ctc_lpa"):
        raise HTTPException(status_code=422, detail="Could not find CTC in the PDF. Please use manual entry.")
    
    # Use defaults if any fields are empty/null from LLM
    role = extracted.get("role") or "Software Engineer"
    city = extracted.get("city") or "Bangalore"
    exp = extracted.get("experience_years") or 0
    
    market = fetch_salary_data(role, city, exp)
    analysis = analyze_offer(extracted, market)
    return build_response(extracted, market, analysis)

@router.post("/manual")
@limiter.limit("10/minute")
async def analyze_manual(request: Request, data: ManualInput):
    extracted = {
        "role": data.role,
        "company": data.company,
        "city": data.city,
        "ctc_lpa": data.ctc_lpa,
        "experience_years": data.experience_years
    }
    
    market = fetch_salary_data(data.role, data.city, data.experience_years)
    analysis = analyze_offer(extracted, market)
    return build_response(extracted, market, analysis)
