from typing import Any

from app.core.base_model import BaseDeviceModel
from app.device_types.nsx_legacy.model import NSXLegacyModel
from app.device_types.pm8000.model import PM8000Model
from app.device_types.bms_narada.model import BMSNaradaModel
from app.device_types.pcs_danfoss.model import PCSDanfossModel


def create_model(config: dict[str, Any]) -> BaseDeviceModel:
    device = config.get("device", {})
    device_type = device.get("type", "generic")

    if device_type == "nsx_legacy":
        return NSXLegacyModel(config)
    if device_type == "pm8000":
        return PM8000Model(config)
    if device_type == "bms_narada":
        return BMSNaradaModel(config)
    if device_type == "pcs_danfoss":
        return PCSDanfossModel(config)

    return BaseDeviceModel(config)