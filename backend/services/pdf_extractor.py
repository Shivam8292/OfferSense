import fitz  # PyMuPDF
from groq import Groq
import os
import json
from dotenv import load_dotenv

# Load environment variables for independent imports/tests
load_dotenv()

def get_groq_client():
    # Instantiate inside function to prevent crash if key is missing during server boot
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
         raise ValueError("GROQ_API_KEY environment variable is not set")
    return Groq(api_key=api_key)

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_offer_details(pdf_bytes: bytes) -> dict:
    raw_text = extract_text_from_pdf(pdf_bytes)
    
    prompt = f"""
You are an expert at reading Indian job offer letters.
Extract the following information from this offer letter text.
Return ONLY a valid JSON object with these exact keys:
- role: job title/designation (string)
- company: company name (string)  
- city: work location city (string)
- ctc_lpa: total CTC in LPA as a number (float). Convert if given in rupees per annum.
- experience_years: years of experience required or candidate's experience (int, default 0 for freshers)

If any field cannot be found, use null.
Return only the JSON, no explanation, no markdown.

Offer Letter Text:
{raw_text[:3000]}
"""
    
    client = get_groq_client()
    import time
    last_error = None
    for attempt in range(2):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.1
            )
            result = response.choices[0].message.content.strip()
            break
        except Exception as e:
            last_error = e
            if attempt == 1:
                raise RuntimeError(f"Groq API details extraction failed after 2 attempts: {str(e)}")
            time.sleep(1)
    
    # Clean up Markdown code block wrapping if LLM returned it
    if result.startswith("```json"):
        result = result[7:]
    if result.startswith("```"):
        result = result[3:]
    if result.endswith("```"):
        result = result[:-3]
    
    result = result.strip()
    
    return json.loads(result)
