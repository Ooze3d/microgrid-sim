import logging
from typing import Any

logger = logging.getLogger("device_server")


class BaseDeviceModel:
    """
    Base class for all virtual device behaviours.

    A model receives events from the Modbus datastore and can update registers
    to simulate physical behaviour.
    """

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.device = config.get("device", {})
        self.name = self.device.get("name", "virtual_device")

    def on_write(self, datastore, address: int, values: list[int]) -> None:
        """
        Called when the Modbus client writes holding registers.
        Override in device-specific models.
        """
        return

    def tick(self, datastore) -> None:
        """
        Called periodically by the server loop.
        Override in device-specific models for dynamic behaviour.
        """
        return

    def log(self, message: str, *args) -> None:
        logger.info("[%s] " + message, self.name, *args)