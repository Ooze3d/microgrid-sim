import random
from typing import Any

from app.core.base_model import BaseDeviceModel


class PCSDanfossModel(BaseDeviceModel):
    def __init__(self, config: dict[str, Any]):
        super().__init__(config)

        behaviour = config.get("behaviour", {})

        self.dynamic = bool(behaviour.get("dynamic", True))

        #self.operation_mode = int(behaviour.get("operation_mode", 0))  # 0 grid-tied, 1 island
        #self.status = int(behaviour.get("status", 4))  # bit 2 = started, bit 3 = fault

        # Logical PCS state.
        # For this first iteration, raw Modbus values are still preserved exactly
        # so that introducing internal state does not change PLC behaviour.

        self.mode = str(behaviour.get("mode", "csi")).lower()
        self.running = bool(behaviour.get("running", False))
        self.fault = bool(behaviour.get("fault", False))
        self.ready = bool(behaviour.get("ready", True))

        # Temporary raw compatibility values.
        # These remain the source for registers 1615 and 43 until the exact
        # Danfoss -> BESS_MB_reading bit mapping is verified.
        self.operation_mode_raw = int(
            behaviour.get("operation_mode_raw", behaviour.get("operation_mode", 0))
        )

        self.status_raw = int(
            behaviour.get("status_raw", behaviour.get("status", 1))
        )

        self.frequency_min = float(behaviour.get("frequency_min", 49.95))
        self.frequency_max = float(behaviour.get("frequency_max", 50.05))

        self.voltage_percent_min = float(behaviour.get("voltage_percent_min", 99.5))
        self.voltage_percent_max = float(behaviour.get("voltage_percent_max", 100.5))

        self.output_voltage_min = float(behaviour.get("output_voltage_min", 398.0))
        self.output_voltage_max = float(behaviour.get("output_voltage_max", 402.0))

        self.active_power_min = float(behaviour.get("active_power_min", 0.0))
        self.active_power_max = float(behaviour.get("active_power_max", 5.0))

        self.rated_current = int(behaviour.get("rated_current", 400))

        self.input_power_limit = int(behaviour.get("input_power_limit", 250))
        self.output_power_limit = int(behaviour.get("output_power_limit", 250))

    def tick(self, datastore) -> None:
        if not self.dynamic:
            return

        frequency = random.uniform(self.frequency_min, self.frequency_max)

        v12_percent = random.uniform(
            self.voltage_percent_min,
            self.voltage_percent_max,
        )
        v23_percent = random.uniform(
            self.voltage_percent_min,
            self.voltage_percent_max,
        )
        v31_percent = random.uniform(
            self.voltage_percent_min,
            self.voltage_percent_max,
        )

        output_voltage = random.uniform(
            self.output_voltage_min,
            self.output_voltage_max,
        )

        active_power = random.uniform(
            self.active_power_min,
            self.active_power_max,
        )

        # COM_BESS_READING:
        # Voltage_Vxx = raw * 420 * 0.0001
        # 10000 => 420 V
        datastore.setValues(3203, [int(v12_percent * 100)])
        datastore.setValues(3204, [int(v23_percent * 100)])
        datastore.setValues(3205, [int(v31_percent * 100)])

        # COM_BESS_READING:
        # Frequency = raw * 0.01
        # 5000 => 50.00 Hz
        datastore.setValues(1, [int(frequency * 100)])

        # COM_BESS_READING:
        # Active_Power = -raw
        datastore.setValues(1508, [self._to_int16(int(active_power))])

        datastore.setValues(1615, [self.operation_mode_raw])

        # bit 2 = started, bit 3 = fault.
        # 4 means started + no fault.
        datastore.setValues(43, [self.status_raw])

        # GVL_Custom.Output_AC = raw * 0.1
        # 4000 => 400.0 V
        datastore.setValues(1107, [int(output_voltage * 10)])

        datastore.setValues(113, [self.rated_current])

        datastore.setValues(1952, [self.input_power_limit])
        datastore.setValues(1953, [self.output_power_limit])
        

    def _to_int16(self, value: int) -> int:
        if value < 0:
            return (1 << 16) + value
        return value & 0xFFFF