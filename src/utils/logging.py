import logging
import logging.config
from pythonjsonlogger import jsonlogger

# Define the logging configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': jsonlogger.JsonFormatter,
            'fmt': '%(asctime)s %(levelname)s %(name)s %(message)s'
        },
        'console': {
            'format': '[%(levelname)s] %(name)s: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'pulse_cse.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
            'formatter': 'json'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file']
    }
}

# Apply the logging configuration
logging.config.dictConfig(LOGGING_CONFIG)

# Create a logger
logger = logging.getLogger(__name__)

def log_error(message, exception=None):
    """
    Log an error message with an optional exception.
    
    Args:
        message (str): The error message.
        exception (Exception, optional): The exception to log. Defaults to None.
    """
    if exception:
        logger.error(message, exc_info=exception)
    else:
        logger.error(message)

def log_info(message):
    """
    Log an info message.
    
    Args:
        message (str): The info message.
    """
    logger.info(message)

def log_warning(message):
    """
    Log a warning message.
    
    Args:
        message (str): The warning message.
    """
    logger.warning(message)

def log_debug(message):
    """
    Log a debug message.
    
    Args:
        message (str): The debug message.
    """
    logger.debug(message)