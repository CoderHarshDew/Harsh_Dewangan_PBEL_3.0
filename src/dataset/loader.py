# Imports

from pathlib import Path
import os
import pandas as pd
from src.core.logger import logger


def load_cicids2017_dataset(dataset_dir:str | Path):
    """Loads dataset files combined as a single DataFrame."""

    files = os.listdir(dataset_dir)
    files = [file for file in files if file.endswith('.csv')]

    df = pd.DataFrame()

    for file in files:
        temp_df = pd.read_csv(Path(dataset_dir, file))

        df = pd.concat([df, temp_df])

        logger.info(f"Loaded CICIDS2017 Dataset file: {file}")

    logger.info("Loaded CICIDS2017 Dataset.")
    return df


if __name__ == '__main__':
    load_cicids2017_dataset('../../dataset/')
