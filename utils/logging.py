import logging
import sys
from config.settings import LOGGING_CONFIG

# Global list to store user-facing logs (INFO level)
ui_logs = []

def setup_logging():
    """Configure logging for the application."""
    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Clear any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create a console handler that sends DEBUG logs to terminal
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    # Create a formatter and add it to the handler
    formatter = logging.Formatter(LOGGING_CONFIG["format"])
    console_handler.setFormatter(formatter)
    
    # Add the handler to the root logger
    root_logger.addHandler(console_handler)
    
    # Create logger for our application
    logger = logging.getLogger("paypal_agent")
    logger.setLevel(logging.DEBUG)
    
    # Create a custom handler to capture INFO logs for UI
    ui_handler = UILogHandler()
    logger.addHandler(ui_handler)
    
    # Reduce verbosity of third-party libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    
    return logger

class UILogHandler(logging.Handler):
    """Custom log handler that captures INFO logs for the UI."""
    
    def __init__(self):
        super().__init__(level=logging.INFO)
    
    def emit(self, record):
        """Add the log record to the UI logs list if it's INFO level or higher."""
        if record.levelno >= logging.INFO:
            # Always emphasize sandbox mode for PayPal operations
            log_message = self.format(record)
            if "paypal" in log_message.lower() or "payment" in log_message.lower():
                log_message = f"[SANDBOX] {log_message}"
            ui_logs.append(log_message)

def get_ui_logs():
    """Get all UI logs and clear the buffer."""
    global ui_logs
    logs = ui_logs.copy()
    ui_logs = []
    return logs
