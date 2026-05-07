import random
from typing import Any

from app.core.base_model import BaseDeviceModel


class NSXLegacyModel(BaseDeviceModel):
    OPEN_COMMAND = 904
    CLOSE_COMMAND = 905
    RESET_COMMAND = 906

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)

        behaviour = config.get("behaviour", {})

        self.breaker_closed = bool(behaviour.get("initial_closed", True))
        self.dynamic = bool(behaviour.get("dynamic", True))

        self.current_min = int(behaviour.get("current_min", 110))
        self.current_max = int(behaviour.get("current_max", 130))

        self.closed_active_power = int(behaviour.get("closed_active_power", 65036))
        self.closed_reactive_power = int(behaviour.get("closed_reactive_power", 65486))
        self.closed_apparent_power = int(behaviour.get("closed_apparent_power", 505))

        self.command = config.get("command", {})
        self.last_plc_open_value = 0
        self.last_plc_close_value = 0
        self.last_plc_reset_value = 0

    def on_write(self, datastore, address: int, values: list[int]) -> None:
        if address <= 8000 < address + len(values):
            idx = 8000 - address
            cmd = values[idx]

            if cmd == self.OPEN_COMMAND:
                self.open(datastore, source="modbus_command_8000")

            elif cmd == self.CLOSE_COMMAND:
                self.close(datastore, source="modbus_command_8000")

            elif cmd == self.RESET_COMMAND:
                self.reset(datastore, source="modbus_command_8000")

    def tick(self, datastore) -> None:
        self._check_plc_command_triggers(datastore)

        if self.dynamic and self.breaker_closed:
            self._apply_closed_dynamic_values(datastore)

    def open(self, datastore, source: str = "unknown") -> None:
        if not self.breaker_closed:
            return

        self.log("OPEN breaker triggered by %s", source)
        self.breaker_closed = False
        self._apply_open_values(datastore)

    def close(self, datastore, source: str = "unknown") -> None:
        if self.breaker_closed:
            return

        self.log("CLOSE breaker triggered by %s", source)
        self.breaker_closed = True
        self._apply_closed_dynamic_values(datastore)

    def reset(self, datastore, source: str = "unknown") -> None:
        self.log("RESET breaker triggered by %s", source)

        datastore.setValues(12004, [0])
        datastore.setValues(12005, [0])
        datastore.setValues(12011, [0])
        datastore.setValues(12012, [0])

    def _check_plc_command_triggers(self, datastore) -> None:
        triggers = self.command.get("plc_triggers", {})

        open_cfg = triggers.get("open")
        close_cfg = triggers.get("close")
        reset_cfg = triggers.get("reset")

        if open_cfg:
            value = self._read_trigger_value(datastore, open_cfg)
            if value == int(open_cfg.get("value", 1)) and self.last_plc_open_value != value:
                self.open(datastore, source=f"plc_trigger_{open_cfg.get('address')}")
            self.last_plc_open_value = value

        if close_cfg:
            value = self._read_trigger_value(datastore, close_cfg)
            if value == int(close_cfg.get("value", 1)) and self.last_plc_close_value != value:
                self.close(datastore, source=f"plc_trigger_{close_cfg.get('address')}")
            self.last_plc_close_value = value

        if reset_cfg:
            value = self._read_trigger_value(datastore, reset_cfg)
            if value == int(reset_cfg.get("value", 1)) and self.last_plc_reset_value != value:
                self.reset(datastore, source=f"plc_trigger_{reset_cfg.get('address')}")
            self.last_plc_reset_value = value

    def _read_trigger_value(self, datastore, trigger_cfg: dict[str, Any]) -> int:
        address = int(trigger_cfg["address"])
        raw_value = datastore.getValues(address, 1)[0]

        bit = trigger_cfg.get("bit")
        if bit is not None:
            return (raw_value >> int(bit)) & 1

        return int(raw_value)

    def _apply_open_values(self, datastore) -> None:
        datastore.setValues(12001, [0])          # status open
        datastore.setValues(12016, [0, 0, 0])    # currents
        datastore.setValues(12038, [0, 0, 0, 0]) # P1/P2/P3/Ptot
        datastore.setValues(12042, [0, 0, 0, 0]) # Q1/Q2/Q3/Qtot
        datastore.setValues(12046, [0, 0, 0, 0]) # S1/S2/S3/Stot

    def _apply_closed_dynamic_values(self, datastore) -> None:
        i1 = random.randint(self.current_min, self.current_max)
        i2 = random.randint(self.current_min, self.current_max)
        i3 = random.randint(self.current_min, self.current_max)

        datastore.setValues(12001, [1])
        datastore.setValues(12016, [i1, i2, i3])

        datastore.setValues(12041, [self.closed_active_power])
        datastore.setValues(12045, [self.closed_reactive_power])
        datastore.setValues(12049, [self.closed_apparent_power])