import argparse
import logging
from pathlib import Path

from pymodbus.server import StartTcpServer

from app.core.config_loader import load_device_config
from app.core.modbus_context import build_context
from app.core.runtime import start_model_runtime

_LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
logger = logging.getLogger("device_server")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one virtual Modbus TCP device")
    parser.add_argument("--config", required=True, help="Path to YAML device config")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format=_LOG_FORMAT)

    config_path = Path(args.config)
    config = load_device_config(config_path)
    device = config["device"]

    context, slave, model = build_context(config)

    # Holding registers datastore
    datastore = slave.store["h"]

    start_model_runtime(
        model=model,
        datastore=datastore,
        interval_seconds=float(device.get("tick_interval", 0.2)),
    )

    logger.info(
        "Starting %s (%s) on %s:%s (unit_id=%s)",
        device["name"],
        device.get("type", "generic"),
        device.get("bind", "0.0.0.0"),
        device.get("port", 502),
        device.get("unit_id", 255),
    )
    logger.info("Loaded %s configured registers", len(config.get("registers", [])))

    StartTcpServer(
        context=context,
        identity=None,
        address=(device.get("bind", "0.0.0.0"), int(device.get("port", 502))),
    )


if __name__ == "__main__":
    main()