import atexit
import sys
from contextlib import contextmanager

from loguru._logger import Core
from loguru._logger import Logger as LoguruLogger


class Logger(LoguruLogger):
    def __init__(self, context: str):
        super().__init__(
            core=Core(),
            exception=None,
            depth=0,
            record=False,
            lazy=False,
            colors=False,
            raw=False,
            capture=True,
            patchers=[],
            extra={"context": context},
        )
        logger_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "[<red>{extra[context]}</red>] <level>{message}</level>"
        )
        self.add(sys.stderr, format=logger_format)
        atexit.register(self.remove)

    def _start_record(self, name: str) -> str:
        return f"activity [{name}] started."

    def _fail_record(self, name: str) -> str:
        return f"activity [{name}] failed."

    def _error_record(self, name: str, err: Exception) -> str:
        return f"activity [{name}] raised error: {err}"

    def _finish_record(self, name: str) -> str:
        return f"activity [{name}] finished."

    @contextmanager
    def activity(self, name: str, with_traceback: bool = True, capture: bool = False):
        try:
            self.info(self._start_record(name))
            yield
        except Exception as e:
            self.error(self._fail_record(name))

            if with_traceback:
                self.opt(exception=e).error(self._error_record(name, e))

            if not capture:
                raise e
        else:
            self.info(self._finish_record(name))
