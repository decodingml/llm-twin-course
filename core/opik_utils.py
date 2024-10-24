import os

import opik
from opik.configurator.configure import OpikConfigurator

from core.config import settings
from core.logger_utils import get_logger

logger = get_logger(__name__)


def configure_opik() -> None:
    if settings.COMET_API_KEY and settings.COMET_PROJECT:
        try:
            client = OpikConfigurator(api_key=settings.COMET_API_KEY)
            default_workspace = client._get_default_workspace()
        except Exception:
            logger.warning(
                "Default workspace not found. Setting workspace to None and enabling interactive mode."
            )
            default_workspace = None

        os.environ["OPIK_PROJECT_NAME"] = settings.COMET_PROJECT

        opik.configure(
            api_key=settings.COMET_API_KEY,
            workspace=default_workspace,
            use_local=False,
            force=True,
        )
        logger.info("Opik configured successfully.")
    else:
        logger.warning(
            "COMET_API_KEY and COMET_PROJECT are not set. Set them to enable prompt monitoring with Opik (powered by Comet ML)."
        )
