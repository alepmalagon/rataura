"""
Error handling utility module for the Rataura application.
"""

import logging
import functools
import traceback
from typing import Any, Callable, TypeVar, cast

# Configure logging
logger = logging.getLogger(__name__)

# Type variables for function signatures
T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])


def handle_exceptions(func: F) -> F:
    """
    Decorator to handle exceptions in functions.
    
    Args:
        func (F): The function to decorate.
    
    Returns:
        F: The decorated function.
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.exception(f"Exception in {func.__name__}: {e}")
            raise
    
    return cast(F, wrapper)


def handle_async_exceptions(func: F) -> F:
    """
    Decorator to handle exceptions in async functions.
    
    Args:
        func (F): The function to decorate.
    
    Returns:
        F: The decorated function.
    """
    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.exception(f"Exception in {func.__name__}: {e}")
            raise
    
    return cast(F, wrapper)


class ESIError(Exception):
    """
    Exception raised for errors in the ESI API.
    """
    
    def __init__(self, message: str, status_code: int = 0):
        """
        Initialize the exception.
        
        Args:
            message (str): The error message.
            status_code (int, optional): The HTTP status code. Defaults to 0.
        """
        self.status_code = status_code
        self.message = message
        super().__init__(self.message)


class AuthError(Exception):
    """
    Exception raised for authentication errors.
    """
    
    def __init__(self, message: str):
        """
        Initialize the exception.
        
        Args:
            message (str): The error message.
        """
        self.message = message
        super().__init__(self.message)


def format_exception(e: Exception) -> str:
    """
    Format an exception for display.
    
    Args:
        e (Exception): The exception to format.
    
    Returns:
        str: The formatted exception.
    """
    return f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"


def format_error_message(e: Exception) -> str:
    """
    Format an error message for display to the user.
    
    Args:
        e (Exception): The exception to format.
    
    Returns:
        str: The formatted error message.
    """
    if isinstance(e, ESIError):
        return f"EVE Online API error: {e.message}"
    elif isinstance(e, AuthError):
        return f"Authentication error: {e.message}"
    else:
        return f"An error occurred: {str(e)}"
