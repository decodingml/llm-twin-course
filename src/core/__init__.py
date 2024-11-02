from . import db, opik_utils
from .logger_utils import get_logger

try:
    from .opik_utils import configure_opik
    configure_opik()
except:
    logger = get_logger(__file__)
    logger.warning("Could not configure Opik.")

__all__ = ["get_logger", "opik_utils", "db"]
