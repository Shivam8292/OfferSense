import os
import sys
from services.ai_analyzer import analyze_offer

def main():
    extracted = {
        "role": "Software Engineer",
        "company": "TCS",
        "city": "Bangalore",
        "ctc_lpa": 6.5,
        "experience_years": 0
    }
    
    market = {
        "avg_ctc": 8.2,
        "p25_ctc": 6.0,
        "p75_ctc": 10.5,
        "source": "AmbitionBox"
    }
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        print("\n[WARNING] GROQ_API_KEY is not configured in backend/.env!")
        print("Please configure your Groq API key to test the AI analyzer's LLM generation.")
        print("\nTest preparation: SUCCESS")
        sys.exit(0)
        
    print("Running analyze_offer through Groq LLM...")
    try:
        analysis = analyze_offer(extracted, market)
        print("\nAI Analysis Result:")
        import pprint
        pprint.pprint(analysis)
        print("\nAI analyzer test: SUCCESS")
    except Exception as e:
        print(f"\nAI analyzer test: FAILED - {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
