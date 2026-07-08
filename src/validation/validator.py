from pathlib import Path
import numpy as np
import pandas as pd
import yaml


def validate_schema(df: pd.DataFrame, schema_path: Path | str = "../../config/validation/validation_shema.yaml") -> None:
    """This function checks if the provided DataFrame is valid or not, and prints how many invalid values the DataFrame has per category.

    Example::

        -----------------\n
        Nan:  0\n
        Inf:  2775\n
        Negative:  2130864\n
        Out of range values:  2792151\n
        -----------------\n
        NOTE: These are number of cell values not rows

    Parameters:
        df (pd.DataFrame): The DataFrame to validate.
        schema_path (Path): Path to the file defining the schema for this DataFrame."""

    try:
        with open(schema_path, 'r') as file:
            schema_cfg = dict(yaml.safe_load(file))
    except FileNotFoundError as e:
        print('Validation Configuration not  found: ', e)
        return None
    except yaml.YAMLError as e:
        print('Error loading the validation configuration: ', e)
        return None

    nan_count = 0
    inf_count = 0
    negative_count = 0
    out_of_range_count = 0
    #
    # for feature_grp in schema_cfg['feature_groups']:
    #     if "Total Fwd Packets" in schema_cfg['feature_groups'][feature_grp]['features']:
    #         return schema_cfg['feature_groups'][feature_grp]['template']

    numeric_df = df.select_dtypes(include='number')

    for col in numeric_df.columns:
        for feature_grp in schema_cfg['feature_groups']:
            if col in schema_cfg['feature_groups'][feature_grp]['features']:
                col_validation = schema_cfg['feature_groups'][feature_grp]['template']['validation']

                if not col_validation['allow_negative']:
                    negative_count += (numeric_df[col] < 0).sum()

                if not col_validation['allow_inf']:
                    inf_count += (numeric_df[col].isin([np.inf, -np.inf])).sum()

                if not col_validation['allow_nan']:
                    nan_count += numeric_df[col].isnull().sum()

                out_of_range_count += (~ numeric_df[col].between(col_validation['minimum'],
                                                               col_validation['maximum'] if col_validation['maximum'] is not None else np.inf)).sum()

    port_validation = schema_cfg['features']['Destination Port']['validation']

    if not port_validation['allow_negative']:
        negative_count += (numeric_df['Destination Port'] < 0).sum()

    if not port_validation['allow_inf']:
        inf_count += (numeric_df['Destination Port'].isin([np.inf, -np.inf])).sum()

    if not port_validation['allow_nan']:
        nan_count += numeric_df['Destination Port'].isnull().sum()

    out_of_range_count += (~ numeric_df['Destination Port'].between(port_validation['minimum'],
                                                    port_validation['maximum'] if port_validation['maximum'] is not None else np.inf)).sum()

    print("Validation Report")
    print("-----------------")
    print("Nan: ", nan_count)
    print("Inf: ", inf_count)
    print("Negative: ", negative_count)
    print("Out of range values: ", out_of_range_count)
    print("-----------------")
    print("NOTE: These are number of cell values not rows")

    return None

