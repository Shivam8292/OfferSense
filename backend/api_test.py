import urllib.request, json

url = "http://127.0.0.1:8000/analyze/manual"
payload = json.dumps({
    "role": "Software Engineer",
    "company": "TCS",
    "city": "Bangalore",
    "ctc_lpa": 6.5,
    "experience_years": 0
}).encode("utf-8")

req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
with urllib.request.urlopen(req, timeout=60) as resp:
    result = json.loads(resp.read())

market = result["market"]
verdict = result["verdict"]
counter = result["counter_offer"]

print("=" * 50)
print("MARKET DATA:")
print("  avg_ctc  = %.1f LPA" % market["avg_ctc"])
print("  p25_ctc  = %.1f LPA" % market["p25_ctc"])
print("  p75_ctc  = %.1f LPA" % market["p75_ctc"])
print("  source   = " + market["source"])
print()
print("VERDICT:")
print("  should_negotiate = " + str(verdict["should_negotiate"]))
print("  pct_diff         = %.1f%%" % verdict["percentage_diff"])
print()
print("COUNTER OFFER: %.1f LPA" % (counter["suggested_ctc"] or 0))
print("=" * 50)
print("FIX CONFIRMED!" if market["avg_ctc"] < 30 else "STILL BROKEN - avg too high!")
