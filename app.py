import os
import sys
from pathlib import Path
from collections import Counter

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from src.ml.random_forest import RandomForest
from src.core.config import config_loader
from src.dataset.loader import load_cicids2017_dataset
from src.preprocessing.preprocessing import PreprocessingPipeline
from src.preprocessing.cleaning import initial_cleanup

MODES = ['train', 'predict', 'help']
VALIDATION_SCHEMA_CFG_PATH = Path('config/preprocessing/validation_shema.yaml')
VALIDATION_RULES_CFG_PATH = Path('config/preprocessing/validation_rules.yaml')
CLEANING_CFG_PATH = Path('config/preprocessing/cleaning.yaml')
RF_HYPERPARAMETERS_PATH = Path('config/ml/rf_hyperparameters.yaml')
PIPELINE_CFG_PATH = Path('config/preprocessing/pipeline.yaml')
REPORT_PATH = Path('reports/')
MODEL_PATH = Path('model/')
ENCODER_PATH = Path('encoder/')

def load_configurations():

    schema_cfg = config_loader(VALIDATION_SCHEMA_CFG_PATH)
    rules_cfg = config_loader(VALIDATION_RULES_CFG_PATH)
    cleaning_cfg = config_loader(CLEANING_CFG_PATH)
    rf_hyperparameters = config_loader(RF_HYPERPARAMETERS_PATH)
    pipeline_cfg = config_loader(PIPELINE_CFG_PATH)

    return schema_cfg, rules_cfg, cleaning_cfg, rf_hyperparameters, pipeline_cfg

def print_prediction(pred: np.ndarray, confidence: np.ndarray, df: pd.DataFrame):
    report_df = df.copy()
    report_df['Prediction'] = pred
    report_df['Confidence'] = confidence
    counts = Counter(pred)
    total = len(pred)
    benign = counts.get('BENIGN', 0)
    malicious = total - benign
    distribution = (
        report_df['Prediction'].value_counts().drop('BENIGN', errors='ignore')
    )
    top = (
        report_df[report_df["Prediction"] != "BENIGN"].sort_values("Confidence", ascending=False).head(10).copy()
    )
    top['flow_id'] = top.index

    print('-' * 15)
    print('Observion Analysis Report')
    print('-' * 15)
    print(f'Flows Analyzed: {total}')
    print()
    print(f"Benign: {benign}")
    print(f'Malicious: {malicious}')
    print(f"Attack Distribution:")
    print('-'*15)
    print(distribution)
    print(f"Top suspicious flows:")
    print('-'*15)
    print(top[['flow_id','Prediction', 'Confidence']])


if __name__ == '__main__':

    args = sys.argv
    print(args)

    if len(args) != 3:
        raise Exception(f'The number of arguments do not match, required 3 got {len(args)}')

    if args[1].lower() not in MODES:
        raise ValueError(f'Mode not recognized: {args[1]}\nAvailable Modes: {MODES}')

    if args[1].lower() == 'help':
        print('Usage syntax:')
        print('python app.py mode dataset_path')
        print(f'Available Modes: {MODES}')
        print("dataset_path is the path to the folder where dataset files are located, all csv files will be loaded.")
        exit()

    dataset_path = Path(args[2])

    if not dataset_path.exists():
        raise FileNotFoundError(f'No such file or directory: {dataset_path}')

    if not dataset_path.is_dir():
        raise NotADirectoryError(f'The provided is not a directory: {dataset_path}')

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

    df = load_cicids2017_dataset(dataset_path)
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
            report_file = Path(REPORT_PATH, f'validation_report_{file_count + 1}')

            with open(report_file, 'w') as file:
                file.write(preprocess.validation_result[f'validation_result_{file_count + 1}'])

    except Exception as e:
        print(f'Error generating the report file: {e}')

    x = df.drop(columns='Label')

    if args[1].lower() == 'train':
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
    elif not Path(MODEL_PATH, 'Random-Forest-1.0.joblib').exists():
        raise FileNotFoundError(f'Model Does not exist: {Path(MODEL_PATH, 'Random-Forest-1.0.joblib')}')
    elif not Path(MODEL_PATH, 'Random-Forest-1.0.joblib').is_file():
        raise IsADirectoryError(f"Model is not a file: {Path(MODEL_PATH, 'Random-Forest-1.0.joblib')}")
    elif not Path(ENCODER_PATH, 'label_encoder_rf.pkl').exists():
        raise FileNotFoundError(f'Model Does not exist: {Path(ENCODER_PATH, 'label_encoder_rf.pkl')}')
    elif not Path(ENCODER_PATH, 'label_encoder_rf.pkl').is_file():
        raise IsADirectoryError(f"Model is not a file: {Path(ENCODER_PATH, 'label_encoder_rf.pkl')}")
    else:
        label_encoder = joblib.load(Path(ENCODER_PATH, 'label_encoder_rf.pkl'))

        model.load(Path(MODEL_PATH, 'Random-Forest-1.0.joblib'))
        print('Model loaded')

        proba = model.predict_proba(x)

        confidence = proba.max(axis=1)
        prediction = label_encoder.inverse_transform(
            model.model.classes_[proba.argmax(axis=1)]
        )

        print_prediction(prediction, confidence, x)
