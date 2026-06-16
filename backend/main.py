from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import analyze
from dotenv import load_dotenv

# Load environmental variables at the very beginning
load_dotenv()

app = FastAPI(title="OfferSense API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router)

@app.get("/health")
def health():
    return {"status": "ok"}
