import logging
import inspect
import os


def _get_caller_info():
    frame = inspect.currentframe()
    caller = inspect.getouterframes(frame)[2]
    filename = os.path.basename(caller.filename)
    line_number = caller.lineno
    caller_name = caller.function
    return f"{filename}:{line_number} - {caller_name}"


class MyLogger:

    def __init__(self, log_level=logging.DEBUG):
        self.log_level = log_level
        self.logger = self._configure_logger()

    def _configure_logger(self):
        logger = logging.getLogger(__name__)

        # Check if the logger has handlers already (which would be the case if it was already instantiated)
        if not logger.handlers:
            logger.setLevel(self.log_level)

            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(self.log_level)
            stream_handler.setFormatter(formatter)

            logger.addHandler(stream_handler)

        return logger

    def info(self, message):
        caller_info = _get_caller_info()
        self.logger.info(f"{caller_info} - {message}")

    def error(self, message):
        caller_info = _get_caller_info()
        self.logger.error(f"{caller_info} - {message}")
