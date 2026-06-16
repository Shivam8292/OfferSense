import httpx
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime, timedelta
import os

# Set DB path relative to the backend folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "offersense.db")

FALLBACK_SALARY_DATA = {
    "software engineer": {"fresher": {"avg": 6.5, "p25": 5.0, "p75": 9.0}, "1-2yr": {"avg": 9.0, "p25": 7.0, "p75": 13.0}},
    "data analyst": {"fresher": {"avg": 5.5, "p25": 4.0, "p75": 7.5}, "1-2yr": {"avg": 7.5, "p25": 6.0, "p75": 10.0}},
    "data scientist": {"fresher": {"avg": 7.0, "p25": 5.5, "p75": 10.0}, "1-2yr": {"avg": 10.0, "p25": 8.0, "p75": 14.0}},
    "product manager": {"fresher": {"avg": 8.0, "p25": 6.0, "p75": 12.0}, "1-2yr": {"avg": 12.0, "p25": 9.0, "p75": 18.0}},
    "business analyst": {"fresher": {"avg": 5.0, "p25": 4.0, "p75": 7.0}, "1-2yr": {"avg": 7.0, "p25": 5.5, "p75": 9.5}},
    "frontend developer": {"fresher": {"avg": 5.5, "p25": 4.5, "p75": 8.0}, "1-2yr": {"avg": 8.0, "p25": 6.5, "p75": 11.0}},
    "backend developer": {"fresher": {"avg": 6.0, "p25": 5.0, "p75": 8.5}, "1-2yr": {"avg": 9.0, "p25": 7.0, "p75": 13.0}},
    "default": {"fresher": {"avg": 6.0, "p25": 4.5, "p75": 8.5}, "1-2yr": {"avg": 8.5, "p25": 6.5, "p75": 12.0}}
}

def get_experience_bucket(years: int) -> str:
    if years <= 0:
        return "fresher"
    elif years <= 2:
        return "1-2yr"
    else:
        return "2-5yr"

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
            source TEXT DEFAULT 'AmbitionBox',
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
    """, (role.lower(), city.lower(), exp_bucket, data["avg_ctc"], data["p25_ctc"], data["p75_ctc"], data.get("source", "AmbitionBox")))
    conn.commit()
    conn.close()

def get_fallback_salary(role: str, exp_bucket: str) -> dict:
    role_lower = role.lower()
    for key in FALLBACK_SALARY_DATA:
        if key in role_lower:
            bucket_data = FALLBACK_SALARY_DATA[key].get(exp_bucket, FALLBACK_SALARY_DATA[key].get("fresher"))
            return {"avg_ctc": bucket_data["avg"], "p25_ctc": bucket_data["p25"], "p75_ctc": bucket_data["p75"], "source": "Internal Benchmark"}
    default = FALLBACK_SALARY_DATA["default"].get(exp_bucket, FALLBACK_SALARY_DATA["default"]["fresher"])
    return {"avg_ctc": default["avg"], "p25_ctc": default["p25"], "p75_ctc": default["p75"], "source": "Internal Benchmark"}

def fetch_salary_data(role: str, city: str, experience_years: int) -> dict:
    init_db()
    exp_bucket = get_experience_bucket(experience_years)
    
    cached = get_cached_salary(role, city, exp_bucket)
    if cached:
        return cached
    
    try:
        role_slug = role.lower().replace(" ", "-")
        url = f"https://www.ambitionbox.com/profile/{role_slug}-salary"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"}
        
        with httpx.Client(timeout=10, follow_redirects=True) as client:
            response = client.get(url, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            # Parse text with AmbitionBox format if possible
            salary_elements = soup.find_all(text=lambda t: "LPA" in str(t) or "lakh" in str(t).lower())
            
            if salary_elements:
                salaries = []
                for elem in salary_elements[:10]:
                    try:
                        num = float(''.join(filter(lambda x: x.isdigit() or x == '.', str(elem))))
                        if 1 < num < 100:
                            salaries.append(num)
                    except:
                        continue
                
                if len(salaries) >= 3:
                    salaries.sort()
                    data = {
                        "avg_ctc": round(sum(salaries) / len(salaries), 1),
                        "p25_ctc": round(salaries[len(salaries)//4], 1),
                        "p75_ctc": round(salaries[3*len(salaries)//4], 1),
                        "source": "AmbitionBox"
                    }
                    save_to_cache(role, city, exp_bucket, data)
                    return data
    except Exception:
        pass
    
    fallback = get_fallback_salary(role, exp_bucket)
    save_to_cache(role, city, exp_bucket, fallback)
    return fallback
