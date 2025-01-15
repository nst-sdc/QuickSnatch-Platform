import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logging(app):
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Set up file handler for general logs
    general_handler = RotatingFileHandler(
        'logs/quicksnatch.log',
        maxBytes=10000000,  # 10MB
        backupCount=5
    )
    general_handler.setLevel(logging.INFO)
    general_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    ))

    # Set up file handler for activity logs
    activity_handler = RotatingFileHandler(
        'logs/activity.log',
        maxBytes=10000000,  # 10MB
        backupCount=5
    )
    activity_handler.setLevel(logging.INFO)
    activity_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] USER:%(user)s ACTION:%(action)s LEVEL:%(level)s STATUS:%(status)s'
    ))

    # Create activity logger
    activity_logger = logging.getLogger('activity')
    activity_logger.setLevel(logging.INFO)
    activity_logger.addHandler(activity_handler)

    # Add handlers to app logger
    app.logger.addHandler(general_handler)
    app.logger.setLevel(logging.INFO)

    return activity_logger

def log_activity(logger, user, action, level=None, status='success'):
    """Log user activity with custom format"""
    logger.info('', extra={
        'user': user,
        'action': action,
        'level': level or 'N/A',
        'status': status
    })
