from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: str | Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(base)

    for key, value in override.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)

    return result


def load_device_config(instance_config_path: str | Path) -> dict[str, Any]:
    instance_config_path = Path(instance_config_path)

    instance_config = load_yaml(instance_config_path)

    device_type = instance_config.get("device", {}).get("type")

    if not device_type:
        raise ValueError("Device config must define device.type")

    default_registers_path = (
        Path("/app/app/device_types")
        / device_type
        / "default_registers.yaml"
    )

    default_config = load_yaml(default_registers_path)

    return deep_merge(default_config, instance_config)