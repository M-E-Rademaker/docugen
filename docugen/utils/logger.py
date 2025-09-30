"""
Logging utilities.
"""

import logging
from rich.logging import RichHandler


def setup_logger(name: str, verbose: bool = False) -> logging.Logger:
    """
    Set up logger with rich handler.

    Parameters
    ----------
    name : str
        Logger name
    verbose : bool
        Enable verbose logging

    Returns
    -------
    logging.Logger
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    handler = RichHandler(rich_tracebacks=True)
    logger.addHandler(handler)

    return logger