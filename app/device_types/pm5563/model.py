import random
from typing import Any

from app.core.base_model import BaseDeviceModel
from app.core.encoding import encode_value


class PM5563Model(BaseDeviceModel):
    def __init__(self, config: dict[str, Any]):
        super().__init__(config)

        behaviour = config.get("behaviour", {})

        self.dynamic = bool(behaviour.get("dynamic", True))

        self.current_min = float(behaviour.get("current_min", 35.0))
        self.current_max = float(behaviour.get("current_max", 55.0))

        self.voltage_min = float(behaviour.get("voltage_min", 398.0))
        self.voltage_max = float(behaviour.get("voltage_max", 405.0))

        self.active_power_min = float(
            behaviour.get("active_power_min", 40.0)
        )
        self.active_power_max = float(
            behaviour.get("active_power_max", 70.0)
        )

        self.reactive_power_min = float(
            behaviour.get("reactive_power_min", 5.0)
        )
        self.reactive_power_max = float(
            behaviour.get("reactive_power_max", 12.0)
        )

        self.apparent_power_min = float(
            behaviour.get("apparent_power_min", 42.0)
        )
        self.apparent_power_max = float(
            behaviour.get("apparent_power_max", 72.0)
        )

        self.frequency_min = float(
            behaviour.get("frequency_min", 49.95)
        )
        self.frequency_max = float(
            behaviour.get("frequency_max", 50.05)
        )

        self.byteorder = config.get("encoding", {}).get(
            "byteorder", "big"
        )
        self.wordorder = config.get("encoding", {}).get(
            "wordorder", "little"
        )

    def tick(self, datastore) -> None:
        if not self.dynamic:
            return

        i1 = random.uniform(self.current_min, self.current_max)
        i2 = random.uniform(self.current_min, self.current_max)
        i3 = random.uniform(self.current_min, self.current_max)

        v12 = random.uniform(self.voltage_min, self.voltage_max)
        v23 = random.uniform(self.voltage_min, self.voltage_max)
        v31 = random.uniform(self.voltage_min, self.voltage_max)

        p = random.uniform(
            self.active_power_min,
            self.active_power_max,
        )

        q = random.uniform(
            self.reactive_power_min,
            self.reactive_power_max,
        )

        s = random.uniform(
            self.apparent_power_min,
            self.apparent_power_max,
        )

        f = random.uniform(
            self.frequency_min,
            self.frequency_max,
        )

        # Request 1
        self._set_float(datastore, 2999, i1)
        self._set_float(datastore, 3001, i2)
        self._set_float(datastore, 3003, i3)

        self._set_float(datastore, 3019, v12)
        self._set_float(datastore, 3021, v23)
        self._set_float(datastore, 3023, v31)

        # Request 2
        self._set_float(datastore, 3059, p)
        self._set_float(datastore, 3067, q)
        self._set_float(datastore, 3075, s)

        # Request 3
        self._set_float(datastore, 3109, f)

    def _set_float(
        self,
        datastore,
        address: int,
        value: float,
    ) -> None:
        words = encode_value(
            register_type="float32",
            value=value,
            byteorder=self.byteorder,
            wordorder=self.wordorder,
        )

        datastore.setValues(address, words)