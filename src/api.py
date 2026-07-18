# Imports

from pathlib import Path
import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from src.backend.routes import router
from src.backend.train_or_predict import train_rf, dependency_check

# Global Variables
FRONTEND_PATH = Path("frontend")
TEMPLATE_PATH = Path(FRONTEND_PATH, "template")
STATIC_PATH = Path(FRONTEND_PATH, "static")
MODEL_PATH = Path("model/Random-Forest-1.0.joblib")

HOST = "0.0.0.0"
PORT = 8000

# App configuration
app = FastAPI(title="Observion", version="1.0")

app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")

templates = Jinja2Templates(directory=TEMPLATE_PATH)

app.include_router(router)


def start_api():
    uvicorn.run(
        "src.api:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@router.get("/system-status")
async def system_status():
    a, b = dependency_check()

    return {
        "model_ready": a,
        "encoder_ready": b
    }

@router.post("/train")
async def train_model():

    train_rf()

    return {
        "message":"Model trained successfully"
    }


if __name__ == "__main__":
    start_api()