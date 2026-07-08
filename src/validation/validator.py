# Imports
from pathlib import Path
import numpy as np
import pandas as pd
import yaml
from src.utilities.evaluator import bind_var_and_evaluate, compile_expr


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
        print('Validation schema not found: ', e)
        return None
    except yaml.YAMLError as e:
        print('Error loading the validation schema: ', e)
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


def validate_rules(df: pd.DataFrame, rules_path: Path | str = "../../config/validation/rules.yaml"):
    """"""

    try:
        with open(rules_path, 'r') as file:
            rules_cfg = dict(yaml.safe_load(file))

    except FileNotFoundError as e:
        print("Validation rules not found: ", e)
        return None
    except yaml.YAMLError as e:
        print("Error processing validation rules: ", e)
        return None

    rule_violations = dict()

    for rule in rules_cfg['rules']:
        rule_violations[rule['id']] = 0

        missing_columns = set(rule['columns']) - set(df.columns)

        if missing_columns:
            raise ValueError(f"Rule {rule['id']} references missing columns: {missing_columns}")

        columns = {
            column: df[column]
            for column in rule['columns']
        }

        exp_f = compile_expr(rule['expression'])

        context = {
            column: columns[column]
            for column in rule['columns']
        }

        if rule['id'] == 'R019':
            context['VALID_LABEL_SET'] = rules_cfg['VALID_LABEL_SET']

        result = bind_var_and_evaluate(exp_f, **context)

        rule_violations[rule['id']] = (~result).sum()


    return rule_violations

if __name__ == "__main__":
    df = pd.DataFrame()
    print(validate_rules(df=df))
    pass