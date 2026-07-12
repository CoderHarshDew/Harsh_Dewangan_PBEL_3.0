from pathlib import Path
import os
import pandas as pd


def load_cicids2017_dataset(dataset_dir:str | Path):

    files = os.listdir(dataset_dir)
    files = [file for file in files if file.endswith('.csv')]

    df = pd.DataFrame()

    for file in files:
        temp_df = pd.read_csv(Path(dataset_dir, file))

        df = pd.concat([df, temp_df])

    return df


if __name__ == '__main__':
    load_cicids2017_dataset('../../dataset/')
