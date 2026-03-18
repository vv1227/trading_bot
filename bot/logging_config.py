"""Logging configuration for the trading bot."""
import logging
import sys
from pathlib import Path
from datetime import datetime
def setup_logging(log_dir: str = "logs") -> logging.Logger:
    """
    Configure logging to both file and console.
    
    Args:
        log_dir: Directory to store log files.
        
    Returns:
        Configured logger instance.
    """
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    log_file = log_path / "trading.log"
    
    logger = logging.getLogger("trading_bot")
    logger.setLevel(logging.DEBUG)
    
    if logger.handlers:
        return logger
    
    file_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    console_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S"
    )
    
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
def get_logger() -> logging.Logger:
    """Get the trading bot logger instance."""
    return logging.getLogger("trading_bot")

