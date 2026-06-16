import fitz
import os
import sys
from services.pdf_extractor import extract_offer_details

def create_dummy_pdf() -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    text = """
    OFFER LETTER
    
    Date: June 15, 2026
    
    Dear Shivam,
    
    We are pleased to offer you the position of Software Engineer at TCS.
    Your annual total compensation (CTC) will be INR 6,50,000 (Six Lakh Fifty Thousand Rupees).
    Your work location will be Bangalore, India.
    This role does not require prior professional experience (0 years of experience).
    
    Best regards,
    TCS HR Team
    """
    page.insert_text((50, 50), text)
    pdf_bytes = doc.write()
    doc.close()
    return pdf_bytes

def main():
    print("Generating dummy PDF...")
    pdf_bytes = create_dummy_pdf()
    
    # Check if GROQ_API_KEY is configured
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        print("\n[WARNING] GROQ_API_KEY is not configured in backend/.env!")
        print("Please replace 'your_groq_api_key_here' with your real Groq API key in backend/.env.")
        print("Once configured, run this script again to test the actual LLM call.")
        print("\nTest PDF generation: SUCCESS")
        sys.exit(0)
        
    print("Calling extract_offer_details with Groq API...")
    try:
        details = extract_offer_details(pdf_bytes)
        print("\nExtracted Details:")
        import pprint
        pprint.pprint(details)
        print("\nPDF extraction test: SUCCESS")
    except Exception as e:
        print(f"\nPDF extraction test: FAILED - {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
