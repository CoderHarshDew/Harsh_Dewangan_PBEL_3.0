from pathlib import Path
import yaml

def load_validation_schema(path: Path | str = '../../config/validation/validation_shema.yaml'):
    """Loads the validation schema.

    Parameters:
        path (Path | str): Optional, path to schema file.

    Returns:
        Validation schema configuration as a dict."""

    try:
        with open(path, 'r') as file:
            cfg = dict(yaml.safe_load(file))
    except FileNotFoundError as e:
        print('Validation schema not found: ', e)
        return None
    except yaml.YAMLError as e:
        print('Error loading the validation schema: ', e)
        return None

    return cfg


def load_validation_rules(path: Path | str = '../../config/validation/rules.yaml'):
    """Loads the validation rules.

    Parameters:
        path (Path | str): Optional, path to rules file.

    Returns:
        Validation rules configuration as a dict."""

    try:
        with open(path, 'r') as file:
            cfg = dict(yaml.safe_load(file))
    except FileNotFoundError as e:
        print('Validation rules not found: ', e)
        return None
    except yaml.YAMLError as e:
        print('Error loading the validation rules: ', e)
        return None

    return cfg

def load_cleaning_configuration(path: Path | str = '../../config/cleaning/cleaning.yaml'):
    """Loads the validation rules.

        Parameters:
            path (Path | str): Optional, path to cleaning configuration.

        Returns:
            Validation rules configuration as a dict."""

    try:
        with open(path, 'r') as file:
            cfg = dict(yaml.safe_load(file))
    except FileNotFoundError as e:
        print('Cleaning configuration not found: ', e)
        return None
    except yaml.YAMLError as e:
        print('Error loading the cleaning configuration: ', e)
        return None

    return cfg