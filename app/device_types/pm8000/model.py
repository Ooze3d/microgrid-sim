import random
from typing import Any

from app.core.base_model import BaseDeviceModel
from app.core.encoding import encode_value

from app.core.plc_client import PLCModbusClient


class PM8000Model(BaseDeviceModel):
    def __init__(self, config: dict[str, Any]):
        super().__init__(config)

        behaviour = config.get("behaviour", {})

        self.dynamic = bool(behaviour.get("dynamic", True))

        self.current_min = float(behaviour.get("current_min", 13.0))
        self.current_max = float(behaviour.get("current_max", 25.0))

        self.voltage_min = float(behaviour.get("voltage_min", 408.0))
        self.voltage_max = float(behaviour.get("voltage_max", 414.0))

        self.active_power_min = float(behaviour.get("active_power_min", 600.0))
        self.active_power_max = float(behaviour.get("active_power_max", 1050.0))

        self.reactive_power_min = float(behaviour.get("reactive_power_min", 80.0))
        self.reactive_power_max = float(behaviour.get("reactive_power_max", 130.0))

        self.apparent_power_min = float(behaviour.get("apparent_power_min", 610.0))
        self.apparent_power_max = float(behaviour.get("apparent_power_max", 1060.0))

        self.frequency_min = float(behaviour.get("frequency_min", 49.90))
        self.frequency_max = float(behaviour.get("frequency_max", 50.05))

        self.energy_in = float(behaviour.get("initial_energy_in", 123456.0))
        self.energy_out = float(behaviour.get("initial_energy_out", 0.0))

        self.byteorder = config.get("encoding", {}).get("byteorder", "big")
        self.wordorder = config.get("encoding", {}).get("wordorder", "little")

        availability = config.get("availability", {})

        self.availability_client = None
        self.availability_address = None
        self.availability_bit = None
        self.availability_value = 1

        # Conservamos el último estado conocido si hay un fallo puntual
        # de comunicación con el NSX.
        self.available = bool(availability.get("initial_available", True))

        host = availability.get("host")

        if host:
            self.availability_client = PLCModbusClient(
                host=str(host),
                port=int(availability.get("port", 502)),
                unit_id=int(availability.get("unit_id", 255)),
                timeout=float(availability.get("timeout", 1.0)),
            )

            self.availability_address = int(
                availability.get("address", 12001)
            )

            bit = availability.get("bit")
            self.availability_bit = int(bit) if bit is not None else None

            self.availability_value = int(
                availability.get("available_value", 1)
            )

    def tick(self, datastore) -> None:
        if not self.dynamic:
            return

        available = self._read_availability()

        if available != self.available:
            self.available = available

            if self.available:
                self.log("Power source AVAILABLE")
            else:
                self.log("Power source UNAVAILABLE - applying zero measurements")

        if not self.available:
            self._apply_zero_values(datastore)
            return

        self._apply_dynamic_values(datastore)

    def _read_availability(self) -> bool:
        if (
            self.availability_client is None
            or self.availability_address is None
        ):
            return True

        raw_value = self.availability_client.read_holding_register(
            self.availability_address
        )

        # Un timeout puntual no cambia el estado eléctrico simulado.
        # Conservamos el último estado conocido.
        if raw_value is None:
            return self.available

        if self.availability_bit is not None:
            raw_value = (
                int(raw_value) >> self.availability_bit
            ) & 1

        return int(raw_value) == self.availability_value

    def _apply_zero_values(self, datastore) -> None:
        # Corrientes
        self._set_float(datastore, 20999, 0.0)
        self._set_float(datastore, 21001, 0.0)
        self._set_float(datastore, 21003, 0.0)

        # Frecuencia
        self._set_float(datastore, 21015, 0.0)

        # Tensiones
        self._set_float(datastore, 21017, 0.0)
        self._set_float(datastore, 21019, 0.0)
        self._set_float(datastore, 21021, 0.0)

        # Potencias
        self._set_float(datastore, 21045, 0.0)
        self._set_float(datastore, 21053, 0.0)
        self._set_float(datastore, 21061, 0.0)

    def _apply_dynamic_values(self, datastore) -> None:
        i1 = random.uniform(self.current_min, self.current_max)
        i2 = random.uniform(self.current_min, self.current_max)
        i3 = random.uniform(self.current_min, self.current_max)

        v12 = random.uniform(self.voltage_min, self.voltage_max)
        v23 = random.uniform(self.voltage_min, self.voltage_max)
        v31 = random.uniform(self.voltage_min, self.voltage_max)

        p_kw = random.uniform(self.active_power_min, self.active_power_max)
        q_kvar = random.uniform(self.reactive_power_min, self.reactive_power_max)
        s_kva = random.uniform(self.apparent_power_min, self.apparent_power_max)

        f = random.uniform(self.frequency_min, self.frequency_max)

        # Rough kWh accumulation. Active power is treated as kW.
        self.energy_in += abs(p_kw) / 3600.0

        # Energy block used by EMO-M PM8000 reading.
        self._set_energy_block(datastore, 3203, int(self.energy_in))

        # Currents
        self._set_float(datastore, 20999, i1)
        self._set_float(datastore, 21001, i2)
        self._set_float(datastore, 21003, i3)

        # Frequency
        self._set_float(datastore, 21015, f)

        # Voltages
        self._set_float(datastore, 21017, v12)
        self._set_float(datastore, 21019, v23)
        self._set_float(datastore, 21021, v31)

        # Powers.
        # EMO-M divides these by 1000:
        # 21045 -> Active_Power
        # 21053 -> Apparent_Power
        # 21061 -> Reactive_Power
        self._set_float(datastore, 21045, p_kw * 1000.0)
        self._set_float(datastore, 21053, s_kva * 1000.0)
        self._set_float(datastore, 21061, q_kvar * 1000.0)

    def _set_float(self, datastore, address: int, value: float) -> None:
        words = encode_value(
            register_type="float32",
            value=value,
            byteorder=self.byteorder,
            wordorder=self.wordorder,
        )
        datastore.set_internal_values(address, words)

    def _set_energy_block(self, datastore, start_address: int, value: int) -> None:
        value = max(0, int(value))

        words = [
            (value >> 48) & 0xFFFF,
            (value >> 32) & 0xFFFF,
            (value >> 16) & 0xFFFF,
            value & 0xFFFF,
            0,
            0,
            0,
            0,
        ]

        datastore.set_internal_values(start_address, words)