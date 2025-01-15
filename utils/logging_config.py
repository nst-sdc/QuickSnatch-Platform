import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging(app):
    """Set up logging configuration for the application"""
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    # Configure main application logger
    file_handler = RotatingFileHandler(
        'logs/quicksnatch.log',
        maxBytes=10240,
        backupCount=10
    )
    
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('QuickSnatch startup')
    
    # Configure activity logger
    activity_logger = logging.getLogger('activity')
    activity_handler = RotatingFileHandler(
        'logs/activity.log',
        maxBytes=10240,
        backupCount=10
    )
    
    activity_formatter = logging.Formatter(
        '%(asctime)s - %(message)s'
    )
    
    activity_handler.setFormatter(activity_formatter)
    activity_handler.setLevel(logging.INFO)
    
    activity_logger.addHandler(activity_handler)
    activity_logger.setLevel(logging.INFO)
    activity_logger.info('Activity logging started')

def log_activity(logger, user, action, **kwargs):
    """
    Log user activity with additional details
    
    Args:
        logger: The logger instance to use
        user: User identifier (username, email, etc.)
        action: The action being performed
        **kwargs: Additional details to log
    """
    details = ' '.join(f"{k}={v}" for k, v in kwargs.items())
    log_entry = f"User: {user} | Action: {action} | {details}"
    logger.info(log_entry)
