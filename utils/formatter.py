import logging


class ColoredFormatter(logging.Formatter):
    """Colored logging formatter"""

    magenta = "\x1b[35;20m"
    blue = "\x1b[34;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format_head = (
        "%(asctime)s - %(name)s - %(levelname)s (%(filename)s:%(lineno)d): "
    )
    format_body = "%(message)s"

    FORMATS = {
        logging.DEBUG: format_head + magenta + format_body + reset,
        logging.INFO: format_head + blue + format_body + reset,
        logging.WARNING: format_head + yellow + format_body + reset,
        logging.ERROR: format_head + red + format_body + reset,
        logging.CRITICAL: format_head + bold_red + format_body + reset,
    }

    def format(self, record):
        """Format the record"""
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
