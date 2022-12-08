import logging
import sys

from pathlib import Path
from typing import Optional


# Set to the git or project level root
ROOT = Path(__file__).resolve().parent.parent


class FilterRelativePath(logging.Filter):
    """
    Logging filter to make paths relative to a fixed root folder
    """

    def filter(self, record):
        path = Path(record.pathname).resolve()
        record.relativepath = str(path.relative_to(ROOT))
        return True


def init_logger(
    name: Optional[str] = None, time: bool = True, filename: bool = True
) -> logging.Logger:
    """
    Create a logger instance for the current module
    """
    if name is None:
        name = __name__

    logger = logging.getLogger(name)

    # Log all messages
    logger.setLevel(logging.INFO)

    if len(logger.handlers) > 0:
        return logger

    # Set up a handler to print to stderr
    handler = logging.StreamHandler()
    parts = []
    if time:
        parts.append("%(asctime)s")
    parts.append("%(levelname)-1s")
    if filename:
        parts.append("%(relativepath)s:%(lineno)d")

    formatter = logging.Formatter(
        fmt=f"[{' '.join(parts)}] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # May be inefficient, but flush on every log call
    logger.handlers[0].addFilter(FilterRelativePath())
    logger.handlers[0].flush = sys.stderr.flush  # type: ignore
    return logger
