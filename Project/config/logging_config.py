# TODO: Import logger from loguru, sys, and Optional from typing
# TODO: Import get_settings from .settings
# TODO: Create setup_logging function that accepts optional log_level parameter
# TODO: Get settings and determine log level (from param or settings.log_level)
# TODO: Remove default logger handler
# TODO: Add stdout console handler with colored format (time, level, name, function, line, message)
# TODO: Add file handler to logs/app.log with rotation (10MB) and retention (30 days)
# TODO: Add agent-specific file handler to logs/agents.log with rotation (5MB) and retention (7 days)
# TODO: Create get_logger function that binds logger with module name


"""
Logging configuration using Loguru.
Provides structured logging with console and file outputs.
"""

import sys
from typing import Optional
from loguru import logger
from pathlib import Path
from .settings import get_settings


def setup_logging(log_level: Optional[str] = None) -> None:
    """
    Setup logging configuration with console and file handlers.
    
    Args:
        log_level: Optional log level override (DEBUG, INFO, WARNING, ERROR)
    """
    settings = get_settings()
    level = log_level or settings.log_level
    
    # Remove default handler
    logger.remove()
    
    # Console handler with colored output
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
        level=level,
        colorize=True,
        backtrace=True,
        diagnose=True
    )
    
    # Ensure logs directory exists
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Main application log file
    logger.add(
        "logs/app.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level=level,
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        backtrace=True,
        diagnose=True
    )
    
    # Agent-specific log file
    logger.add(
        "logs/agents.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level=level,
        rotation="5 MB",
        retention="7 days",
        compression="zip",
        filter=lambda record: "agent" in record["name"].lower(),
        backtrace=True
    )
    
    logger.info(f"Logging initialized at {level} level")


def get_logger(name: str):
    """
    Get a logger instance bound to a specific module.
    
    Args:
        name: Module name for the logger
        
    Returns:
        Logger instance bound to the module name
    """
    return logger.bind(name=name)
