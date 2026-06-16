from groq import Groq
import os
import json
from dotenv import load_dotenv

# Load env variables for local imports/tests
load_dotenv()

def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set")
    return Groq(api_key=api_key)

def analyze_offer(extracted: dict, market: dict) -> dict:
    user_ctc = extracted.get("ctc_lpa", 0)
    avg_ctc = market.get("avg_ctc", 0)
    p75_ctc = market.get("p75_ctc", 0)
    
    pct_diff = round(((user_ctc - avg_ctc) / avg_ctc) * 100, 1) if avg_ctc else 0
    should_negotiate = user_ctc < avg_ctc
    
    prompt = f"""
You are an expert salary negotiation coach for Indian tech professionals.

Candidate's offer details:
- Role: {extracted.get('role')}
- Company: {extracted.get('company')}
- City: {extracted.get('city')}
- Offered CTC: ₹{user_ctc} LPA
- Experience: {extracted.get('experience_years', 0)} years

Market data for this role:
- Market Average: ₹{avg_ctc} LPA
- Bottom 25%: ₹{market.get('p25_ctc')} LPA
- Top 25%: ₹{p75_ctc} LPA

The offer is {abs(pct_diff)}% {'below' if should_negotiate else 'above'} market average.

Generate a JSON response with exactly these keys:
{{
  "verdict_reasoning": "2-3 sentence explanation of whether to negotiate and why, specific to their role/city/company",
  "counter_offer_ctc": <suggested CTC as float, or null if should not negotiate>,
  "counter_offer_rationale": "1 sentence explaining the counter offer amount",
  "email_script": "Complete professional email to HR. Start with Subject line. Use [HR Name] as placeholder. Specific to their role and company. Confident but professional tone. Ask for the counter offer amount specifically.",
  "verbal_script": "3-4 bullet points of what to say verbally when HR asks about expectations. Practical, direct, no fluff."
}}

Rules:
- If offer is above market, still write email/verbal scripts but frame them as thank you + acceptance with minor asks (joining bonus, WFH flexibility)
- Counter offer should be between market avg and P75, rounded to nearest 0.5 LPA
- Scripts must mention the specific role, city, and if possible, company name
- No generic advice — be specific and actionable
- Return ONLY valid JSON, no markdown, no explanation
"""

    client = get_groq_client()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500,
        temperature=0.3
    )
    
    result_text = response.choices[0].message.content.strip()
    
    # Strip markdown block formatting if present
    if result_text.startswith("```json"):
        result_text = result_text[7:]
    if result_text.startswith("```"):
        result_text = result_text[3:]
    if result_text.endswith("```"):
        result_text = result_text[:-3]
        
    result_text = result_text.strip()
    result = json.loads(result_text)
    
    return {
        "verdict": {
            "should_negotiate": should_negotiate,
            "percentage_diff": pct_diff,
            "reasoning": result["verdict_reasoning"]
        },
        "counter_offer": {
            "suggested_ctc": result.get("counter_offer_ctc"),
            "rationale": result.get("counter_offer_rationale")
        },
        "script": {
            "email": result.get("email_script"),
            "verbal": result.get("verbal_script")
        }
    }
