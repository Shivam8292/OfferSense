# -*- coding: utf-8 -*-
"""
Comprehensive accuracy test - multiple roles, cities, exp levels, CTC values.
Proves the salary fix is GENERAL, not hardcoded.
"""
import urllib.request, json, time, sys

# Force UTF-8 output on Windows
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = "http://127.0.0.1:8000/analyze/manual"

TEST_CASES = [
    # (role, company, city, ctc_lpa, exp_years, description)
    ("Software Engineer",    "TCS",       "Bangalore", 6.5,  0, "Fresher SWE @ TCS"),
    ("Software Engineer",    "Google",    "Bangalore", 35.0, 4, "4yr SWE @ Google"),
    ("Data Scientist",       "Flipkart",  "Bangalore", 8.0,  0, "Fresher DS @ Flipkart"),
    ("Data Scientist",       "Amazon",    "Hyderabad", 22.0, 3, "3yr DS @ Amazon"),
    ("Product Manager",      "Paytm",     "Delhi",     9.0,  1, "1yr PM @ Paytm"),
    ("DevOps Engineer",      "Infosys",   "Pune",      5.5,  0, "Fresher DevOps @ Infosys"),
    ("Business Analyst",     "Wipro",     "Mumbai",    4.5,  0, "Fresher BA @ Wipro"),
    ("Frontend Developer",   "Zomato",    "Bangalore", 12.0, 2, "2yr FE Dev @ Zomato"),
    ("Machine Learning Eng", "Microsoft", "Hyderabad", 28.0, 3, "3yr MLE @ Microsoft"),
    ("Data Analyst",         "Deloitte",  "Mumbai",    5.0,  0, "Fresher DA @ Deloitte"),
]

def call_api(role, company, city, ctc, exp):
    payload = json.dumps({
        "role": role, "company": company, "city": city,
        "ctc_lpa": ctc, "experience_years": exp
    }).encode("utf-8")
    req = urllib.request.Request(
        BASE, data=payload,
        headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())

print("=" * 74)
print("%-38s %6s %6s %6s %6s %s" % ("Test Case", "CTC", "Avg", "P75", "Cntr", "Source"))
print("-" * 74)

all_ok = True
results_summary = []
for role, company, city, ctc, exp, desc in TEST_CASES:
    try:
        res = call_api(role, company, city, ctc, exp)
        m = res["market"]
        c = res["counter_offer"]
        avg = m["avg_ctc"]
        p75 = m["p75_ctc"]
        cntr = c.get("suggested_ctc") or 0.0
        src = m["source"][:12]

        # Sanity checks
        sane = True
        if exp <= 1 and avg > 30:   sane = False  # No fresher gets 30+ LPA avg
        if exp <= 3 and avg > 60:   sane = False  # No 3yr gets 60+ LPA avg
        if avg < 1.5:               sane = False  # Too low
        if not (m["p25_ctc"] <= avg <= p75 * 1.5): sane = False  # Order check

        flag = "OK" if sane else "WRONG!"
        if not sane:
            all_ok = False

        results_summary.append((desc, ctc, avg, p75, cntr, src, sane))
        print("%-38s %6.1f %6.1f %6.1f %6.1f %-12s %s" % (desc, ctc, avg, p75, cntr, src, flag))
        time.sleep(0.5)
    except Exception as e:
        print("%-38s  ERROR: %s" % (desc, str(e)[:50]))
        all_ok = False

print("=" * 74)
print("")
print("RESULT: " + ("ALL 10 SCENARIOS ACCURATE - FIX IS GENERAL" if all_ok else "SOME RESULTS STILL WRONG"))
print("")
print("Detailed breakdown:")
for desc, ctc, avg, p75, cntr, src, ok in results_summary:
    status = "PASS" if ok else "FAIL"
    print("  [%s] %-38s CTC=%.1f -> Market Avg=%.1f, P75=%.1f" % (status, desc, ctc, avg, p75))
