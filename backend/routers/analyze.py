from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from services.pdf_extractor import extract_offer_details
from services.salary_fetcher import fetch_salary_data
from services.ai_analyzer import analyze_offer
import json

router = APIRouter(prefix="/analyze", tags=["analyze"])

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
async def analyze_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files accepted")
    
    pdf_bytes = await file.read()
    
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
async def analyze_manual(data: ManualInput):
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
