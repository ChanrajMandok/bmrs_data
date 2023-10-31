import os

from bmrs.decorators import logger


def aiohttp_params_required(func):
    """
    Decorator that checks for required TIMEOUT, MAX_CONCURRENT_TASKS and MAX_TRIES 
    variables and updates the kwargs of the wrapped function with these variables if they exist.
    """
    def wrapper(*args, **kwargs):
        
        # List of expected environment variables
        env_vars = ['TIMEOUT', 'MAX_TRIES', 'MAX_CONCURRENT_TASKS', 'RATE_LIMIT_SLEEP_TIME']
        env_data = {}

        for var in env_vars:
            value = os.getenv(var)
            
            if not value:
                logger.warning(f"Environment variable {var} is missing or empty")
                continue  # Continue checking the next variable
            
            try:
                # Convert to integer
                int_value = int(value)
                env_data[var.lower()] = int_value
                
            except ValueError:
                logger.error(f"Environment variable {var} is not a valid integer: {value}")
                continue  # Continue checking the next variable

        kwargs.update(env_data)

        return func(*args, **kwargs)
        
    return wrapper