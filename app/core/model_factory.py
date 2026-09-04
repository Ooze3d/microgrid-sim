from typing import Any

from app.core.base_model import BaseDeviceModel
from app.device_types.nsx_legacy.model import NSXLegacyModel
from app.device_types.pm5563.model import PM5563Model
from app.device_types.pm8000.model import PM8000Model
from app.device_types.bms_narada.model import BMSNaradaModel
from app.device_types.pcs_danfoss.model import PCSDanfossModel
from app.device_types.ev_ingeteam.model import EVIngeteamModel


def create_model(config: dict[str, Any]) -> BaseDeviceModel:
    device = config.get("device", {})
    device_type = device.get("type", "generic")

    if device_type == "nsx_legacy":
        return NSXLegacyModel(config)
    if device_type == "pm5563":
        return PM5563Model(config)
    if device_type == "pm8000":
        return PM8000Model(config)
    if device_type == "bms_narada":
        return BMSNaradaModel(config)
    if device_type == "pcs_danfoss":
        return PCSDanfossModel(config)
    if device_type == "ev_ingeteam":
        return EVIngeteamModel(config)

    return BaseDeviceModel(config)