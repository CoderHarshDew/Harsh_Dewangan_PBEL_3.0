# Imports

import os
from collections import Counter
from pathlib import Path
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from src.ml.random_forest import RandomForest
from src.core.config import config_loader
from src.dataset.loader import load_cicids2017_dataset
from src.preprocessing.preprocessing import PreprocessingPipeline
from src.preprocessing.cleaning import initial_cleanup

# Global Variables
VALIDATION_SCHEMA_CFG_PATH = Path('config/preprocessing/validation_shema.yaml')
VALIDATION_RULES_CFG_PATH = Path('config/preprocessing/validation_rules.yaml')
CLEANING_CFG_PATH = Path('config/preprocessing/cleaning.yaml')
RF_HYPERPARAMETERS_PATH = Path('config/ml/rf_hyperparameters.yaml')
PIPELINE_CFG_PATH = Path('config/preprocessing/pipeline.yaml')
REPORT_PATH = Path('reports/')
MODEL_PATH = Path('model/')
ENCODER_PATH = Path('encoder/')
DATASET_PATH = Path('dataset/')

# Dependency Check
def dependency_check():
    model_ready = False
    encoder_ready = False
    if (MODEL_PATH / "Random-Forest-1.0.joblib").exists() and (MODEL_PATH / "Random-Forest-1.0.joblib").is_file():
        model_ready = True
    if (ENCODER_PATH / 'label_encoder_rf.pkl').exists() and (ENCODER_PATH / 'label_encoder_rf.pkl').is_file():
        encoder_ready = True

    return model_ready, encoder_ready



def load_configurations():
    """Loads all configurations."""

    schema_cfg = config_loader(VALIDATION_SCHEMA_CFG_PATH)
    rules_cfg = config_loader(VALIDATION_RULES_CFG_PATH)
    cleaning_cfg = config_loader(CLEANING_CFG_PATH)
    rf_hyperparameters = config_loader(RF_HYPERPARAMETERS_PATH)
    pipeline_cfg = config_loader(PIPELINE_CFG_PATH)

    return schema_cfg, rules_cfg, cleaning_cfg, rf_hyperparameters, pipeline_cfg

def train_rf():
    """Trains a random forest model. Saves it to the MODEL_PATH dir. Uses DATASET_PATH's dataset files for training."""

    schema_cfg, rules_cfg, cleaning_cfg, rf_hyperparameters, pipeline_cfg = load_configurations()

    if not all([schema_cfg, rules_cfg, cleaning_cfg, rf_hyperparameters, pipeline_cfg]):
        raise Exception('Error loading configurations, check logs for more details.')

    hyperparameters = {
        param: rf_hyperparameters[param]
        for param in rf_hyperparameters
        if rf_hyperparameters[param] is not None
    }

    print('Config loading done.')

    model = RandomForest(**hyperparameters)

    print('Model initialized.')

    df = load_cicids2017_dataset(DATASET_PATH)
    print('Data Loaded')

    df = initial_cleanup(df, cleaning_cfg)

    preprocess = PreprocessingPipeline(schema_cfg, rules_cfg, cleaning_cfg)

    for i in range(pipeline_cfg['cycles']):
        preprocess.validate(df)
        df = preprocess.clean(df)

    print('Data cleanup done.')

    try:
        if pipeline_cfg['generate_report']:
            REPORT_PATH.mkdir(parents=True, exist_ok=True)
            file_count = len(os.listdir(REPORT_PATH))
            report_file = Path(REPORT_PATH, f'validation_report_{file_count + 1}.txt')

            with open(report_file, 'w') as file:
                file.write(
                    preprocess.validation_result[f'validation_result_{len(preprocess.validation_result)}'].__str__())

    except Exception as e:
        print(f'Error generating the report file: {e}')

    x = df.drop(columns='Label')

    label_encoder = LabelEncoder()

    y = label_encoder.fit_transform(df["Label"])
    ENCODER_PATH.mkdir(exist_ok=True, parents=True)
    MODEL_PATH.mkdir(exist_ok=True, parents=True)

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42, stratify=y)
    print('Training Model')
    model.fit(x_train, y_train)

    model.save(Path(MODEL_PATH, 'Random-Forest-1.0.joblib'))
    joblib.dump(label_encoder, Path(ENCODER_PATH, 'label_encoder_rf.pkl'))
    print('Model trained and saved')
    
def predict(df: pd.DataFrame) -> dict:
    """Preprocesses and makes a prediction on the provided dataset."""
    
    
    schema_cfg, rules_cfg, cleaning_cfg, rf_hyperparameters, pipeline_cfg = load_configurations()
    

    if not all([schema_cfg, rules_cfg, cleaning_cfg, rf_hyperparameters, pipeline_cfg]):
        raise Exception('Error loading configurations, check logs for more details.')

    preprocess = PreprocessingPipeline(schema_cfg, rules_cfg, cleaning_cfg)
    
    df = initial_cleanup(df, cleaning_cfg)

    for i in range(pipeline_cfg["cycles"]):
        preprocess.validate(df)
        df = preprocess.clean(df)

    x = df.drop(columns="Label")

    model = RandomForest()
    model.load(MODEL_PATH / "Random-Forest-1.0.joblib")

    encoder = joblib.load(ENCODER_PATH / "label_encoder_rf.pkl")


    proba = model.predict_proba(x)

    confidence = proba.max(axis=1)

    prediction = encoder.inverse_transform(
        model.model.classes_[proba.argmax(axis=1)]
    )

    report_df = x.copy()
    report_df["Prediction"] = prediction
    report_df["Confidence"] = confidence

    counts = Counter(prediction)

    total = len(prediction)

    benign = counts.get("BENIGN", 0)

    malicious = total - benign

    distribution = report_df["Prediction"].value_counts().drop("BENIGN", errors="ignore")

    top = report_df[
        report_df["Prediction"] != "BENIGN"
        ].sort_values(
        "Confidence",
        ascending=False
    ).head(10).copy()

    top["flow_id"] = top.index

    predictions = []

    for index, row in report_df.iterrows():
        predictions.append(
            {
                "flow_id": int(index),
                "prediction": row["Prediction"],
                "confidence": float(row["Confidence"])
            }
        )

    top_flows = []

    for _, row in top.iterrows():
        top_flows.append(
            {
                "flow_id": int(row["flow_id"]),
                "prediction": row["Prediction"],
                "confidence": float(row["Confidence"])
            }
        )

    return {
        "summary": {
            "flows": total,
            "benign": benign,
            "malicious": malicious,
            "average_confidence": float(confidence.mean())
        },
        "distribution": {
            attack: int(count)
            for attack, count in distribution.items()
        },
        "confidence_histogram": confidence.tolist(),
        "top_flows": top_flows,
        "predictions": predictions
    }

if __name__ == '__main__':
    train_rf()
