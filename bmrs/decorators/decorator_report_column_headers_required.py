import os

from bmrs.decorators import logger


def report_column_headers_required(func):
    """
    Decorator that checks for required B1770_COLUMN and B1780_COLUMN environment variables 
    and updates the kwargs of the wrapped function with these variables if they exist.
    """
    def wrapper(*args, **kwargs):
        
        # List of expected environment variables
        env_vars = ['B1770_COLUMN', 'B1780_COLUMN']
        env_data = {}

        for var in env_vars:
            value = os.getenv(var)
            
            if not value:
                logger.error(f"Environment variable {var} is missing or empty")
                continue  # Continue checking the next variable
            
            # Provide the value as-is without converting
            env_data[var.lower()] = value

        kwargs.update(env_data)

        return func(*args, **kwargs)
        
    return wrapper
