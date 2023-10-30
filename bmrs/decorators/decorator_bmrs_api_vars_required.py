import os

from bmrs.decorators import logger


def bmrs_api_vars_required(func):
    """
    Decorator that checks for required BMRS environment variables and updates 
    the kwargs of the wrapped function with these variables if they exist.
    """
    def wrapper(*args, **kwargs):
        
        # List of expected environment variables
        env_vars = ['API_SCRIPTING_KEY', 'HOST', 'VERSION', 'URL_END_STR']
        bmrs_constants = {}

        for var in env_vars:
            value = os.getenv(var)
            if not value:
                logger.error(f"Environment variable {var} is missing or empty")
            else:
                # Convert env var name to the expected key format
                key_name = '_'.join(word.lower() for word in var.split())
                bmrs_constants[key_name] = str(value)  # Ensure the value is a string

        kwargs.update(bmrs_constants)

        return func(*args, **kwargs)
        
    return wrapper