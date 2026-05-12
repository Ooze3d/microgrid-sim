import logging
import threading
import time

logger = logging.getLogger("device_server")


def start_model_runtime(model, datastore, interval_seconds: float = 0.2) -> None:
    thread = threading.Thread(
        target=_runtime_loop,
        args=(model, datastore, interval_seconds),
        daemon=True,
    )
    thread.start()


def _runtime_loop(model, datastore, interval_seconds: float) -> None:
    logger.info("Starting runtime loop for model: %s", model.name)

    while True:
        try:
            model.tick(datastore)
        except Exception as exc:
            logger.exception("Runtime loop error: %s", exc)

        time.sleep(interval_seconds)