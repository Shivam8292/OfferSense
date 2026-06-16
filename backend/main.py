from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from routers import analyze
from dotenv import load_dotenv
import traceback

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

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Print the exception traceback to console logs
    traceback.print_exc()
    # Return 500 error formatted inside the FastAPI context (retaining CORS headers)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Server Error: {str(exc)}"}
    )

app.include_router(analyze.router)

@app.get("/health")
def health():
    return {"status": "ok"}
