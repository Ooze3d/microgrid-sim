import logging
from typing import Optional

from pymodbus.client import ModbusTcpClient

logger = logging.getLogger("device_server")


class PLCModbusClient:
    def __init__(self, host: str, port: int = 502, unit_id: int = 255, timeout: float = 1.0):
        self.host = host
        self.port = port
        self.unit_id = unit_id
        self.timeout = timeout
        self.client: Optional[ModbusTcpClient] = None

    def _ensure_connected(self) -> bool:
        if self.client is None:
            self.client = ModbusTcpClient(
                host=self.host,
                port=self.port,
                timeout=self.timeout,
            )

        if not self.client.connected:
            return self.client.connect()

        return True

    def read_holding_register(self, address: int) -> Optional[int]:
        try:
            if not self._ensure_connected():
                logger.warning("Could not connect to PLC %s:%s", self.host, self.port)
                return None

            result = self.client.read_holding_registers(
                address=address,
                count=1,
                slave=self.unit_id,
            )

            if result.isError():
                logger.warning("PLC read error at address %s: %s", address, result)
                return None

            return int(result.registers[0])

        except TypeError:
            # Compatibility fallback for older/newer pymodbus signatures.
            result = self.client.read_holding_registers(
                address=address,
                count=1,
                unit=self.unit_id,
            )

            if result.isError():
                logger.warning("PLC read error at address %s: %s", address, result)
                return None

            return int(result.registers[0])

        except Exception as exc:
            logger.warning("PLC read exception at address %s: %s", address, exc)
            return None