"""
Salary Fetcher Service
-----------------------
Fetches real Indian market salary benchmarks for a given role, city, and experience.

Strategy:
1. Check SQLite cache (valid for 7 days).
2. If cache miss — query Groq LLM with a targeted prompt to get accurate salary data.
3. Validate LLM response for sanity (all values must be realistic LPA figures).
4. If LLM fails or returns garbage — fall back to a hardcoded benchmark table
   built from real AmbitionBox / Glassdoor / Levels.fyi data (Jun 2025).
5. Cache the result and return.
"""

import sqlite3
import json
import os
import re
import time
from datetime import datetime, timedelta
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "offersense.db")

# ──────────────────────────────────────────────────────────────
# STATIC FALLBACK BENCHMARKS (India market, Jun 2025)
# Source: AmbitionBox, Glassdoor, Levels.fyi, Naukri Salary Insights
# Format: role → exp_bucket → {avg, p25, p75}  (all in LPA)
# ──────────────────────────────────────────────────────────────
FALLBACK_SALARY_DATA = {
    # ── Software / Engineering ──────────────────────────────────
    "software engineer": {
        "fresher":  {"avg": 6.0,  "p25": 4.0,  "p75": 8.5},
        "1-2yr":    {"avg": 9.5,  "p25": 7.0,  "p75": 13.0},
        "2-5yr":    {"avg": 16.0, "p25": 12.0, "p75": 22.0},
        "5yr+":     {"avg": 28.0, "p25": 20.0, "p75": 40.0},
    },
    "software developer": {
        "fresher":  {"avg": 5.5,  "p25": 3.5,  "p75": 8.0},
        "1-2yr":    {"avg": 8.5,  "p25": 6.5,  "p75": 12.0},
        "2-5yr":    {"avg": 14.0, "p25": 10.0, "p75": 20.0},
        "5yr+":     {"avg": 25.0, "p25": 18.0, "p75": 35.0},
    },
    "frontend developer": {
        "fresher":  {"avg": 5.0,  "p25": 3.5,  "p75": 7.0},
        "1-2yr":    {"avg": 8.0,  "p25": 6.0,  "p75": 11.0},
        "2-5yr":    {"avg": 14.0, "p25": 10.0, "p75": 20.0},
        "5yr+":     {"avg": 24.0, "p25": 16.0, "p75": 35.0},
    },
    "backend developer": {
        "fresher":  {"avg": 5.5,  "p25": 4.0,  "p75": 7.5},
        "1-2yr":    {"avg": 9.0,  "p25": 7.0,  "p75": 12.0},
        "2-5yr":    {"avg": 15.0, "p25": 11.0, "p75": 21.0},
        "5yr+":     {"avg": 26.0, "p25": 18.0, "p75": 38.0},
    },
    "full stack developer": {
        "fresher":  {"avg": 5.5,  "p25": 4.0,  "p75": 8.0},
        "1-2yr":    {"avg": 9.0,  "p25": 7.0,  "p75": 13.0},
        "2-5yr":    {"avg": 16.0, "p25": 12.0, "p75": 22.0},
        "5yr+":     {"avg": 27.0, "p25": 19.0, "p75": 38.0},
    },
    "senior software engineer": {
        "fresher":  {"avg": 8.0,  "p25": 6.0,  "p75": 11.0},
        "1-2yr":    {"avg": 14.0, "p25": 10.0, "p75": 20.0},
        "2-5yr":    {"avg": 22.0, "p25": 16.0, "p75": 32.0},
        "5yr+":     {"avg": 35.0, "p25": 25.0, "p75": 50.0},
    },
    # ── Data / AI / ML ─────────────────────────────────────────
    "data analyst": {
        "fresher":  {"avg": 4.5,  "p25": 3.0,  "p75": 6.5},
        "1-2yr":    {"avg": 7.0,  "p25": 5.0,  "p75": 10.0},
        "2-5yr":    {"avg": 12.0, "p25": 8.0,  "p75": 17.0},
        "5yr+":     {"avg": 20.0, "p25": 14.0, "p75": 28.0},
    },
    "data scientist": {
        "fresher":  {"avg": 7.0,  "p25": 5.0,  "p75": 10.0},
        "1-2yr":    {"avg": 12.0, "p25": 9.0,  "p75": 16.0},
        "2-5yr":    {"avg": 20.0, "p25": 14.0, "p75": 28.0},
        "5yr+":     {"avg": 32.0, "p25": 22.0, "p75": 45.0},
    },
    "machine learning engineer": {
        "fresher":  {"avg": 8.0,  "p25": 6.0,  "p75": 11.0},
        "1-2yr":    {"avg": 14.0, "p25": 10.0, "p75": 20.0},
        "2-5yr":    {"avg": 24.0, "p25": 17.0, "p75": 34.0},
        "5yr+":     {"avg": 38.0, "p25": 26.0, "p75": 55.0},
    },
    "ai engineer": {
        "fresher":  {"avg": 8.5,  "p25": 6.0,  "p75": 12.0},
        "1-2yr":    {"avg": 15.0, "p25": 11.0, "p75": 22.0},
        "2-5yr":    {"avg": 26.0, "p25": 18.0, "p75": 38.0},
        "5yr+":     {"avg": 42.0, "p25": 28.0, "p75": 60.0},
    },
    # ── Product / Design ────────────────────────────────────────
    "product manager": {
        "fresher":  {"avg": 8.0,  "p25": 6.0,  "p75": 12.0},
        "1-2yr":    {"avg": 14.0, "p25": 10.0, "p75": 20.0},
        "2-5yr":    {"avg": 24.0, "p25": 17.0, "p75": 35.0},
        "5yr+":     {"avg": 38.0, "p25": 26.0, "p75": 55.0},
    },
    "ui ux designer": {
        "fresher":  {"avg": 4.0,  "p25": 2.5,  "p75": 6.0},
        "1-2yr":    {"avg": 6.5,  "p25": 5.0,  "p75": 9.0},
        "2-5yr":    {"avg": 11.0, "p25": 8.0,  "p75": 15.0},
        "5yr+":     {"avg": 18.0, "p25": 13.0, "p75": 25.0},
    },
    # ── Business / Finance ──────────────────────────────────────
    "business analyst": {
        "fresher":  {"avg": 5.0,  "p25": 3.5,  "p75": 7.0},
        "1-2yr":    {"avg": 7.5,  "p25": 5.5,  "p75": 10.0},
        "2-5yr":    {"avg": 12.0, "p25": 9.0,  "p75": 17.0},
        "5yr+":     {"avg": 20.0, "p25": 14.0, "p75": 28.0},
    },
    "financial analyst": {
        "fresher":  {"avg": 5.5,  "p25": 4.0,  "p75": 7.5},
        "1-2yr":    {"avg": 8.0,  "p25": 6.0,  "p75": 11.0},
        "2-5yr":    {"avg": 13.0, "p25": 9.0,  "p75": 18.0},
        "5yr+":     {"avg": 22.0, "p25": 15.0, "p75": 32.0},
    },
    # ── QA / Testing ────────────────────────────────────────────
    "qa engineer": {
        "fresher":  {"avg": 4.0,  "p25": 3.0,  "p75": 5.5},
        "1-2yr":    {"avg": 6.5,  "p25": 5.0,  "p75": 9.0},
        "2-5yr":    {"avg": 10.0, "p25": 7.5,  "p75": 14.0},
        "5yr+":     {"avg": 16.0, "p25": 12.0, "p75": 22.0},
    },
    # ── DevOps / Cloud ──────────────────────────────────────────
    "devops engineer": {
        "fresher":  {"avg": 6.0,  "p25": 4.5,  "p75": 8.0},
        "1-2yr":    {"avg": 10.0, "p25": 7.5,  "p75": 13.5},
        "2-5yr":    {"avg": 17.0, "p25": 12.0, "p75": 24.0},
        "5yr+":     {"avg": 28.0, "p25": 20.0, "p75": 40.0},
    },
    "cloud engineer": {
        "fresher":  {"avg": 6.5,  "p25": 5.0,  "p75": 9.0},
        "1-2yr":    {"avg": 11.0, "p25": 8.0,  "p75": 15.0},
        "2-5yr":    {"avg": 18.0, "p25": 13.0, "p75": 25.0},
        "5yr+":     {"avg": 30.0, "p25": 21.0, "p75": 42.0},
    },
    # ── Default ─────────────────────────────────────────────────
    "default": {
        "fresher":  {"avg": 5.5,  "p25": 3.5,  "p75": 8.0},
        "1-2yr":    {"avg": 9.0,  "p25": 6.5,  "p75": 13.0},
        "2-5yr":    {"avg": 15.0, "p25": 10.0, "p75": 22.0},
        "5yr+":     {"avg": 25.0, "p25": 16.0, "p75": 36.0},
    },
}

# Sanity bounds — any LPA value outside these is rejected
MIN_LPA = 1.5
MAX_LPA = 200.0


def get_experience_bucket(years: int) -> str:
    if years <= 0:
        return "fresher"
    elif years <= 2:
        return "1-2yr"
    elif years <= 5:
        return "2-5yr"
    else:
        return "5yr+"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS salary_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            city TEXT NOT NULL,
            experience_bucket TEXT NOT NULL,
            avg_ctc REAL,
            p25_ctc REAL,
            p75_ctc REAL,
            source TEXT DEFAULT 'LLM',
            cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def get_cached_salary(role: str, city: str, exp_bucket: str):
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("""
        SELECT avg_ctc, p25_ctc, p75_ctc, source, cached_at FROM salary_cache
        WHERE LOWER(role)=? AND LOWER(city)=? AND experience_bucket=?
        ORDER BY cached_at DESC LIMIT 1
    """, (role.lower(), city.lower(), exp_bucket)).fetchone()
    conn.close()
    if row:
        try:
            cached_at = datetime.fromisoformat(row[4])
        except ValueError:
            cached_at = datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S")
        if datetime.now() - cached_at < timedelta(days=7):
            return {"avg_ctc": row[0], "p25_ctc": row[1], "p75_ctc": row[2], "source": row[3]}
    return None


def save_to_cache(role: str, city: str, exp_bucket: str, data: dict):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT INTO salary_cache (role, city, experience_bucket, avg_ctc, p25_ctc, p75_ctc, source)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (role.lower(), city.lower(), exp_bucket,
          data["avg_ctc"], data["p25_ctc"], data["p75_ctc"],
          data.get("source", "LLM")))
    conn.commit()
    conn.close()


def is_sane(data: dict, exp_bucket: str) -> bool:
    """Reject values that are clearly wrong (too high for freshers, etc.)."""
    avg = data.get("avg_ctc", 0)
    p25 = data.get("p25_ctc", 0)
    p75 = data.get("p75_ctc", 0)

    # All values must be within global bounds
    for v in [avg, p25, p75]:
        if not (MIN_LPA <= v <= MAX_LPA):
            return False

    # p25 ≤ avg ≤ p75 ordering check (allow small tolerance)
    if not (p25 <= avg * 1.5 and avg <= p75 * 1.5):
        return False

    # Fresher hard cap — no Indian fresher realistically gets > 30 LPA (FAANG exceptions aside)
    if exp_bucket == "fresher" and avg > 30:
        return False

    # 1-2yr cap
    if exp_bucket == "1-2yr" and avg > 50:
        return False

    return True


def get_fallback_salary(role: str, exp_bucket: str) -> dict:
    role_lower = role.lower()
    best_key = None
    best_len = 0
    for key in FALLBACK_SALARY_DATA:
        if key == "default":
            continue
        if key in role_lower and len(key) > best_len:
            best_key = key
            best_len = len(key)

    table = FALLBACK_SALARY_DATA.get(best_key or "default", FALLBACK_SALARY_DATA["default"])
    bucket_data = table.get(exp_bucket) or table.get("fresher")
    return {
        "avg_ctc": bucket_data["avg"],
        "p25_ctc": bucket_data["p25"],
        "p75_ctc": bucket_data["p75"],
        "source": "Internal Benchmark",
    }


def fetch_salary_via_llm(role: str, city: str, exp_bucket: str) -> dict | None:
    """Ask Groq LLM for current Indian market salary benchmarks."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None

    exp_label = {
        "fresher": "a fresh graduate / 0 years experience",
        "1-2yr":   "1-2 years of experience",
        "2-5yr":   "2-5 years of experience",
        "5yr+":    "5+ years of experience",
    }.get(exp_bucket, "0 years experience")

    prompt = f"""You are an expert in Indian tech job market salaries (2024-2025 data).
Give me the realistic salary benchmarks (in LPA — Lakhs Per Annum) for:

Role: {role}
City: {city}
Experience: {exp_label}

Return ONLY a valid JSON object with these exact keys:
- avg_ctc: market average CTC in LPA (float, realistic)
- p25_ctc: 25th percentile CTC in LPA (float, i.e. lower-end salaries)
- p75_ctc: 75th percentile CTC in LPA (float, i.e. top-25% salaries)

Use real data from AmbitionBox, Glassdoor, Naukri. Be realistic — for a fresher Software Engineer in India, the average is typically 5-8 LPA, NOT 50 LPA.

Return only the JSON object, no markdown, no explanation."""

    try:
        client = Groq(api_key=api_key)
        for attempt in range(2):
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200,
                    temperature=0.1,
                )
                text = response.choices[0].message.content.strip()
                # Strip markdown if present
                text = re.sub(r"```json\s*", "", text)
                text = re.sub(r"```\s*", "", text)
                data = json.loads(text)
                data = {
                    "avg_ctc": float(data["avg_ctc"]),
                    "p25_ctc": float(data["p25_ctc"]),
                    "p75_ctc": float(data["p75_ctc"]),
                    "source": "AI Market Data",
                }
                if is_sane(data, exp_bucket):
                    return data
                # If not sane, fall through to fallback
                return None
            except Exception:
                if attempt == 0:
                    time.sleep(1)
    except Exception:
        pass
    return None


def fetch_salary_data(role: str, city: str, experience_years: int) -> dict:
    """Main entry point — returns salary benchmark for the given role/city/exp."""
    init_db()
    exp_bucket = get_experience_bucket(experience_years)

    # 1. Cache hit
    cached = get_cached_salary(role, city, exp_bucket)
    if cached:
        return cached

    # 2. LLM lookup
    llm_data = fetch_salary_via_llm(role, city, exp_bucket)
    if llm_data:
        save_to_cache(role, city, exp_bucket, llm_data)
        return llm_data

    # 3. Static fallback
    fallback = get_fallback_salary(role, exp_bucket)
    save_to_cache(role, city, exp_bucket, fallback)
    return fallback
