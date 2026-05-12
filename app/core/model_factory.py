from typing import Any

from app.core.base_model import BaseDeviceModel
from app.device_types.nsx_legacy.model import NSXLegacyModel


def create_model(config: dict[str, Any]) -> BaseDeviceModel:
    device = config.get("device", {})
    device_type = device.get("type", "generic")

    if device_type == "nsx_legacy":
        return NSXLegacyModel(config)

    return BaseDeviceModel(config)