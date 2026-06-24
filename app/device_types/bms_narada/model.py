import random
from typing import Any

from app.core.base_model import BaseDeviceModel


class BMSNaradaModel(BaseDeviceModel):
    def __init__(self, config: dict[str, Any]):
        super().__init__(config)

        behaviour = config.get("behaviour", {})

        self.dynamic = bool(behaviour.get("dynamic", True))

        self.voltage_min = float(behaviour.get("voltage_min", 775.0))
        self.voltage_max = float(behaviour.get("voltage_max", 785.0))

        self.current_min = float(behaviour.get("current_min", 5.0))
        self.current_max = float(behaviour.get("current_max", 25.0))

        self.soc = float(behaviour.get("soc", 70.0))
        self.soh = float(behaviour.get("soh", 98.0))

        self.temp_min = float(behaviour.get("temp_min", 23.0))
        self.temp_max = float(behaviour.get("temp_max", 28.0))

        self.energy_charged = int(behaviour.get("energy_charged", 1000))
        self.energy_discharged = int(behaviour.get("energy_discharged", 500))

    def tick(self, datastore) -> None:
        if not self.dynamic:
            return

        voltage = random.uniform(self.voltage_min, self.voltage_max)
        current = random.uniform(self.current_min, self.current_max)
        temp = random.uniform(self.temp_min, self.temp_max)

        datastore.setValues(4103, [0])  # Operation state: normal
        datastore.setValues(4105, [0])  # Fault/alarm state: no alarms

        datastore.setValues(4109, [int(voltage * 10)])
        datastore.setValues(4110, [int(current * 10)])

        datastore.setValues(4111, [int(self.soc * 10)])
        datastore.setValues(4112, [int(self.soh * 10)])

        datastore.setValues(4137, [int(temp * 10)])

        self.energy_discharged += 1

        datastore.setValues(4145, [(self.energy_charged >> 16) & 0xFFFF])
        datastore.setValues(4146, [self.energy_charged & 0xFFFF])

        datastore.setValues(4147, [(self.energy_discharged >> 16) & 0xFFFF])
        datastore.setValues(4148, [self.energy_discharged & 0xFFFF])