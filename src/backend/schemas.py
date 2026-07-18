# Imports

from pydantic import BaseModel
from typing import Dict, List


class Summary(BaseModel):
    flows: int
    benign: int
    malicious: int
    average_confidence: float


class FlowPrediction(BaseModel):
    flow_id: int
    prediction: str
    confidence: float


class PredictionResponse(BaseModel):
    summary: Summary
    distribution: Dict[str, int]
    confidence_histogram: List[float]
    top_flows: List[FlowPrediction]
    predictions: List[FlowPrediction]