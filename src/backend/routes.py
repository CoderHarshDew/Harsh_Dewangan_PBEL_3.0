# Imports

from fastapi import APIRouter, UploadFile, File
import pandas as pd
from src.backend.train_or_predict import predict
from src.backend.upload import validate_upload
from src.backend.schemas import PredictionResponse


#Router Setup
router = APIRouter()


@router.post("/predict",response_model=PredictionResponse)
async def prediction_route(file: UploadFile = File(...)):
    file = await validate_upload(file)

    df = pd.read_csv(file.file)

    result = predict(df)

    return result