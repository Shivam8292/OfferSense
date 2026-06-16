from services.salary_fetcher import fetch_salary_data, get_fallback_salary

print("=== FALLBACK DATA TEST ===")
r1 = get_fallback_salary("Software Engineer", "fresher")
print("Fresher SWE: avg=%s p25=%s p75=%s" % (r1["avg_ctc"], r1["p25_ctc"], r1["p75_ctc"]))

r2 = get_fallback_salary("Software Engineer", "1-2yr")
print("1-2yr SWE:   avg=%s p25=%s p75=%s" % (r2["avg_ctc"], r2["p25_ctc"], r2["p75_ctc"]))

r3 = get_fallback_salary("Data Scientist", "fresher")
print("Fresher DS:  avg=%s p25=%s p75=%s" % (r3["avg_ctc"], r3["p25_ctc"], r3["p75_ctc"]))

r4 = get_fallback_salary("Business Analyst", "fresher")
print("Fresher BA:  avg=%s p25=%s p75=%s" % (r4["avg_ctc"], r4["p25_ctc"], r4["p75_ctc"]))

print("\n=== FULL FETCH TEST (with LLM + cache) ===")
r5 = fetch_salary_data("Software Engineer", "Bangalore", 0)
print("Fetch SWE Fresher Bangalore: avg=%s p25=%s p75=%s source=%s" % (r5["avg_ctc"], r5["p25_ctc"], r5["p75_ctc"], r5["source"]))
