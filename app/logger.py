import logging
import os
import sys

import logging_loki


LOKI_URL = os.getenv("LOKI_URL", "http://loki-gateway.loki.svc.cluster.local")
APP_NAME = os.getenv("APP_NAME", "fastapi-app")


def get_logger(name: str = "app") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # stdout handler (always on)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    )
    logger.addHandler(stdout_handler)

    # Loki handler — pushes logs directly to Loki HTTP API
    loki_handler = logging_loki.LokiHandler(
        url=f"{LOKI_URL}/loki/api/v1/push",
        tags={"app": APP_NAME},
        version="1",
    )
    logger.addHandler(loki_handler)

    return logger
