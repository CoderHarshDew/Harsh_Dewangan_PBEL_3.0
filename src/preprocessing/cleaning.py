import pandas as pd
from src.core.evaluator import bind_var_and_evaluate, compile_expr
from src.preprocessing.result import ValidationResult


def clean(validation_result: ValidationResult, df: pd.DataFrame, cleaning_cfg: dict) -> pd.DataFrame:
    """Cleans a DataFrame based on validation result and a cleaning configuration.

    :param validation_result: Validation result of DataFrame, detailing invalid entries to clean.
    :param df: The DataFrame to clean.
    :param cleaning_cfg: The configuration file defining cleaning rules.
    :return: Cleaned DataFrame
    """

    df.drop(index=validation_result.non_repairable, inplace=True)

    for col in cleaning_cfg['repairable']:
        formula = cleaning_cfg['formulas'][cleaning_cfg['repairable'][col]['formula']]

        missing_columns = set(formula['requires']) - set(df.columns)

        if missing_columns:
            raise ValueError(f"Computing column: {col}\nRequires missing columns: {missing_columns}")

        expr = compile_expr(formula['expression'])

        context = {
            col: df[col]
            for col in formula['requires']
        }

        rows = list(validation_result.repairable)

        result = bind_var_and_evaluate(expr, **context)
        df.loc[rows, col] = result.loc[rows]

    return df

if __name__ == "__main__":
    pass