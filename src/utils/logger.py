from logging import Logger as _Logger, getLogger, StreamHandler, Formatter, DEBUG, INFO, WARNING, ERROR, CRITICAL

class Logger:
    def __init__(self, name: str, level: int = INFO):
        self.logger = getLogger(name)
        self.logger.setLevel(level)
        handler = StreamHandler()
        handler.setFormatter(Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)

    def debug(self, message: str):
        self.logger.debug(message)

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)

    def critical(self, message: str):
        self.logger.critical(message)