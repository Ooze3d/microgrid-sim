import logging

from pymodbus.datastore import ModbusSequentialDataBlock

logger = logging.getLogger("device_server")


class InteractiveDataBlock(ModbusSequentialDataBlock):
    """
    Modbus datastore that forwards write events to a device model.
    """

    def __init__(self, address, values, model):
        super().__init__(address, values)
        self.model = model

    def setValues(self, address, values):
        super().setValues(address, values)

        logger.debug(
            "Write received: address=%s values=%s",
            address,
            values,
        )

        try:
            self.model.on_write(self, address, values)

        except Exception as exc:
            logger.exception(
                "Error while processing device interaction: %s",
                exc,
            )