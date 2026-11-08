import sys
from loguru import logger
from app.core.config import settings

def configure_logging() ->None:
    logger.remove()
    log_format= (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "request_id={extra[request_id]} | "
        "<level>{message}</level>"

    )
    logger.configure(extra={"request_id":"-"})
    logger.add(
        sys.stdout,
        format = log_format,
        level = "DEBUG" if settings.debug else "INFO",
        backtrace=False,
        diagnose = False,
        serialize = settings.environment=="production"



    )