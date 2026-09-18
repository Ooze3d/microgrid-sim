import time
from typing import Any

from app.core.base_model import BaseDeviceModel
from app.core.encoding import encode_value


class EVIngeteamModel(BaseDeviceModel):

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)

        self._last_tick = time.time()
        self._energy_wh = 2500.0

    def tick(self, datastore) -> None:
        # datastore remains HR for compatibility with all existing models.
        # Ingeteam measurements live in Input Registers.
        ir = self.input_datastore

        if ir is None:
            return

        now = time.time()
        dt = now - self._last_tick
        self._last_tick = now

        # -----------------------------------------------------
        # Outlet 1
        # -----------------------------------------------------

        state_1 = 5       # Charging
        power_1 = 11000   # W

        self._energy_wh += power_1 * dt / 3600.0

        self._set_ir(
            ir,
            address=1,
            register_type="uint16",
            value=state_1,
        )

        self._set_ir(
            ir,
            address=2,
            register_type="uint32",
            value=power_1,
            wordorder="little",
        )

        self._set_ir(
            ir,
            address=4,
            register_type="uint32",
            value=int(self._energy_wh),
            wordorder="little",
        )

        # -----------------------------------------------------
        # Outlet 2
        # -----------------------------------------------------

        self._set_ir(
            ir,
            address=101,
            register_type="uint16",
            value=1,      # Available
        )

        self._set_ir(
            ir,
            address=102,
            register_type="uint32",
            value=0,
            wordorder="little",
        )

        self._set_ir(
            ir,
            address=104,
            register_type="uint32",
            value=0,
            wordorder="little",
        )

        # -----------------------------------------------------
        # Plant totals
        # -----------------------------------------------------

        phase_1 = power_1 // 3
        phase_2 = power_1 // 3
        phase_3 = power_1 - phase_1 - phase_2

        self._set_ir(
            ir,
            address=9000,
            register_type="int32",
            value=phase_1,
            wordorder="big",
        )

        self._set_ir(
            ir,
            address=9002,
            register_type="int32",
            value=phase_2,
            wordorder="big",
        )

        self._set_ir(
            ir,
            address=9004,
            register_type="int32",
            value=phase_3,
            wordorder="big",
        )

        self._set_ir(
            ir,
            address=9006,
            register_type="int32",
            value=1,
            wordorder="big",
        )

    def _set_ir(
        self,
        datastore,
        address: int,
        register_type: str,
        value,
        wordorder: str = "big",
    ) -> None:

        words = encode_value(
            register_type=register_type,
            value=value,
            byteorder="big",
            wordorder=wordorder,
        )

        # Ingeteam documentation uses 1-based register addresses.
        # With pymodbus zero_mode=False, store the value one position higher
        # so an external request for register N returns the documented register N.
        internal_address = address + 1

        datastore.set_internal_values(internal_address, words)

        # Temporary diagnostic mirror, if still enabled
        if self.config.get("diagnostics", {}).get(
            "mirror_input_to_holding",
            False,
        ):
            self.holding_datastore.set_internal_values(internal_address, words)