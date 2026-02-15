"""
Logging Configuration
"""
import logging
import sys


def setup_logging(log_level: str = "INFO"):
    """Configure application logging"""
    
    # Create logger
    logger = logging.getLogger("integmed")
    logger.setLevel(getattr(logging, log_level))
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level))
    
    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler
    logger.addHandler(console_handler)
    
    return logger


# Global logger instance - will be initialized after config is loaded
logger = None
