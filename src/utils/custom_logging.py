import copy
import logging

LOG_COLORS = {
    logging.INFO: "\033[32m",  # GREEN
    logging.ERROR: "\033[31m",  # RED
    logging.WARNING: "\033[33m",  # YELLOW
}

RESET = "\033[0m"


class ColorFormatter(logging.Formatter):
    """Custom log formatter that applies color formatting to log records."""

    def format(self, record: logging.LogRecord, *args: tuple, **kwargs: tuple) -> str:
        """Applies color formatting to log records."""
        new_record = copy.copy(record)
        if new_record.levelno in LOG_COLORS:
            new_record.levelname = f"{LOG_COLORS[new_record.levelno]}{new_record.levelname}{RESET}"
        return super().format(new_record, *args, **kwargs)


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Sets up logging with color formatting for console output.

    Args:
        level (int): The logging level (default is logging.INFO).

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(__name__)

    if not logger.hasHandlers():
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(level)
        stream_handler.setFormatter(
            ColorFormatter(
                fmt="%(asctime)s | %(filename)-35s | %(lineno)-3d | %(levelname)s : %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        logger.addHandler(stream_handler)

    logger.setLevel(level)
    return logger


logger = setup_logging()
