"""
Create a global logger
"""
import re
import sys
import logging


class ConsoleStyle:
    """ Console coloring and styles """
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    CRITICAL = '\033[31m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'  # Stop all styling


class DebugLogFormats:
    """ Log formats for use for different log levels """
    DEFAULT = '%(asctime)s [%(levelname)s] %(name)s - %(message)s'
    ERROR = '%(asctime)s [{}%(levelname)s{}] %(name)s - %(message)s'.format(ConsoleStyle.ERROR,
                                                                            ConsoleStyle.END)
    CRITICAL = '%(asctime)s [{}%(levelname)s{}] %(name)s - %(message)s'.format(
            ConsoleStyle.CRITICAL,
            ConsoleStyle.END
        )
    WARNING = '%(asctime)s [{}%(levelname)s{}] %(name)s - %(message)s'.format(ConsoleStyle.WARNING,
                                                                              ConsoleStyle.END)
    INFO = '%(asctime)s [{}%(levelname)s{}] %(name)s - %(message)s'.format(ConsoleStyle.OKGREEN,
                                                                           ConsoleStyle.END)
    DEBUG = '%(asctime)s [{}%(levelname)s{}] %(name)s - %(message)s'.format(ConsoleStyle.OKBLUE,
                                                                            ConsoleStyle.END)


class LogFormats:
    """ Log formats for use for different log levels """
    DEFAULT = '%(levelname)s \t %(message)s'
    ERROR = '{}%(levelname)s{} \t %(message)s'.format(ConsoleStyle.ERROR, ConsoleStyle.END)
    CRITICAL = '{}%(levelname)s{} \t %(message)s'.format(
            ConsoleStyle.CRITICAL,
            ConsoleStyle.END
        )
    WARNING = '{}%(levelname)s{} \t %(message)s'.format(ConsoleStyle.WARNING, ConsoleStyle.END)
    INFO = '{}%(levelname)s{} \t\t %(message)s'.format(ConsoleStyle.OKGREEN, ConsoleStyle.END)
    DEBUG = '{}%(levelname)s{} \t %(message)s'.format(ConsoleStyle.OKBLUE, ConsoleStyle.END)


class ColoredStyle:
    """ Text styling for the ColoredFormatter.

        Based on: https://github.com/python/cpython/blob/master/Lib/logging/__init__.py#L426
    """
    default_format = '%(message)s'
    asctime_format = '%(asctime)s'
    asctime_search = '%(asctime)'
    validation_pattern = re.compile(r'%\(\w+\)[#0+ -]*(\*|\d+)?(\.(\*|\d+))?[diouxefgcrsa%]', re.I)

    def __init__(self):
        if '-d' in sys.argv:
            self._fmt = DebugLogFormats.DEFAULT
        else:
            self._fmt = LogFormats.DEFAULT

    def usesTime(self):
        return self._fmt.find(self.asctime_search) >= 0

    def validate(self):
        """Validate the input format, ensure it matches the correct style"""
        if not self.validation_pattern.search(self._fmt):
            raise ValueError("Invalid format '{}' for '{}' style".format(self._fmt,
                                                                         self.default_format[0]))

    def _format(self, record):
        formats = LogFormats
        if '-d' in sys.argv:
            formats = DebugLogFormats
        if record.levelno == logging.ERROR:
            return formats.ERROR % record.__dict__
        elif record.levelno == logging.WARNING:
            return formats.WARNING % record.__dict__
        elif record.levelno == logging.INFO:
            return formats.INFO % record.__dict__
        elif record.levelno == logging.CRITICAL:
            return formats.CRITICAL % record.__dict__
        elif record.levelno == logging.DEBUG:
            return formats.DEBUG % record.__dict__
        return self._fmt % record.__dict__

    def format(self, record):
        try:
            return self._format(record)
        except KeyError as e:
            raise ValueError('Formatting field not found in record: %s' % e)


class ColoredFormatter(logging.Formatter):
    """ Formatter that will use the ColoredStyle class """
    def __init__(self, fmt=None, datefmt=None, style='%', validate=True):
        self._style = ColoredStyle()
        if validate:
            self._style.validate()

        self._fmt = self._style._fmt
        self.datefmt = datefmt


parent_logger = logging.getLogger()

# Create and add a handler for console output
console_handler = logging.StreamHandler()
formatter = ColoredFormatter()
console_handler.setFormatter(formatter)
parent_logger.addHandler(console_handler)


def setDebugLogging():
    console_handler.setLevel(logging.DEBUG)
    parent_logger.setLevel(logging.DEBUG)


if '-d' in sys.argv:
    setDebugLogging()
else:
    console_handler.setLevel(logging.INFO)
    parent_logger.setLevel(logging.INFO)


def getLogger(name):
    return parent_logger.getChild(name)


def loggingShutdown():
    return logging.shutdown()
