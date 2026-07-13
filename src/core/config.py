from pathlib import Path
import yaml
from src.core.logger import logger

def load_validation_schema(path: Path | str = '../../config/preprocessing/validation_shema.yaml'):
    """Loads the preprocessing schema.

    Parameters:
        path (Path | str): Optional, path to schema file.

    Returns:
        Validation schema configuration as a dict."""

    try:
        with open(path, 'r') as file:
            cfg = dict(yaml.safe_load(file))
    except FileNotFoundError as e:
        logger.exception(f"Validation schema not found")
        return None
    except yaml.YAMLError as e:
        logger.exception(f"Error loading the validation schema")
        return None

    logger.info(f"Successfully loaded the validation schema.")
    return cfg


def load_validation_rules(path: Path | str = '../../config/preprocessing/validation_rules.yaml'):
    """Loads the preprocessing rules.

    Parameters:
        path (Path | str): Optional, path to rules file.

    Returns:
        Validation rules configuration as a dict."""

    try:
        with open(path, 'r') as file:
            cfg = dict(yaml.safe_load(file))
    except FileNotFoundError as e:
        logger.exception(f"Validation rules not found")
        return None
    except yaml.YAMLError as e:
        logger.exception(f"Error loading the validation rules"
                         f"")
        return None

    logger.info(f"Successfully loaded the validation rules.")
    return cfg

def load_cleaning_configuration(path: Path | str = '../../config/preprocessing/cleaning.yaml'):
    """Loads the preprocessing rules.

        Parameters:
            path (Path | str): Optional, path to cleaning configuration.

        Returns:
            Validation rules configuration as a dict."""

    try:
        with open(path, 'r') as file:
            cfg = dict(yaml.safe_load(file))
    except FileNotFoundError as e:
        logger.exception(f"Cleaning configuration not found.")
        return None
    except yaml.YAMLError as e:
        logger.exception(f"Error loading the cleaning configuration")
        return None

    logger.info(f"Successfully loaded the cleaning configuration.")
    return cfg