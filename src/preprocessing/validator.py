# Imports
import numpy as np
import pandas as pd
from src.core.evaluator import bind_var_and_evaluate, compile_expr
from src.preprocessing.result import SchemaResult, RuleResult


def validate_schema(df: pd.DataFrame, schema_cfg: dict) -> SchemaResult:
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
        schema_cfg (dict): The schema configuration file."""

    schema_result = SchemaResult()

    numeric_df = df.select_dtypes(include='number')

    for col in numeric_df.columns:
        for feature_grp in schema_cfg['feature_groups']:
            if col in schema_cfg['feature_groups'][feature_grp]['features']:
                col_validation = schema_cfg['feature_groups'][feature_grp]['template']['validation']
                invalid = set()

                if not col_validation['allow_negative']:
                    negative_mask = (numeric_df[col] < 0) & (~ numeric_df[col].isin(col_validation['sentinel']))
                    invalid.update(np.flatnonzero(negative_mask))
                    schema_result.negative_count += negative_mask.sum()

                if not col_validation['allow_inf']:
                    inf_mask = numeric_df[col].isin([np.inf, -np.inf])
                    invalid.update(np.flatnonzero(inf_mask))
                    schema_result.inf_count += inf_mask.sum()

                if not col_validation['allow_nan']:
                    nan_mask = numeric_df[col].isnull()
                    invalid.update(np.flatnonzero(nan_mask))
                    schema_result.nan_count += nan_mask.sum()


                out_of_range_mask = ~ numeric_df[col].between(col_validation['minimum'],
                                                               col_validation['maximum'] if col_validation['maximum'] is not None else np.inf)
                invalid.update(np.flatnonzero(out_of_range_mask))
                schema_result.out_of_range_count += out_of_range_mask.sum()

                schema_result.invalid[col] = invalid

    port_validation = schema_cfg['features']['Destination Port']['validation']

    invalid_dp = set()

    if not port_validation['allow_negative']:
        negative_dp_mask = (numeric_df['Destination Port'] < 0) &  (~ numeric_df['Destination Port'].isin(port_validation['sentinel']))
        invalid_dp.update(np.flatnonzero(negative_dp_mask))
        schema_result.negative_count += negative_dp_mask.sum()

    if not port_validation['allow_inf']:
        inf_dp_mask = numeric_df['Destination Port'].isin([np.inf, -np.inf])
        invalid_dp.update(np.flatnonzero(inf_dp_mask))
        schema_result.inf_count += inf_dp_mask.sum()

    if not port_validation['allow_nan']:
        nan_dp_mask = numeric_df['Destination Port'].isnull()
        invalid_dp.update(np.flatnonzero(nan_dp_mask))
        schema_result.nan_count += nan_dp_mask.sum()

    out_of_range_dp_mask = ~ numeric_df['Destination Port'].between(port_validation['minimum'],
                                                    port_validation['maximum'] if port_validation['maximum'] is not None else np.inf)
    invalid_dp.update(np.flatnonzero(out_of_range_dp_mask))
    schema_result.out_of_range_count += out_of_range_dp_mask.sum()
    schema_result.invalid['Destination Port'] = invalid_dp

    schema_result.invalid['Label'] = set()


    return schema_result


def validate_rules(df: pd.DataFrame, rules_cfg: dict) -> RuleResult:
    """This function checks if the provided DataFrame follows the right rules, counts numer of times a rule has been violated, and returns the value.

    Parameters:
        df (pd.DataFrame): The DataFrame to validate.
        rules_cfg (dict): The rules configuration file.

    Returns:
        Rule violation count as a dict"""

    rule_result = RuleResult()

    for rule in rules_cfg['rules']:
        rule_result.violator_counts[rule['id']] = 0

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

        result = ~ bind_var_and_evaluate(exp_f, **context)
        rule_result.violators[rule['id']] = set(np.flatnonzero(result))
        rule_result.violator_counts[rule['id']] = result.sum()


    return rule_result

if __name__ == "__main__":
    pass