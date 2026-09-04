import logging
from typing import Any

from app.core.encoding import encode_value

logger = logging.getLogger("device_server")


def build_block_maps(
    config: dict[str, Any],
) -> tuple[dict[int, int], dict[int, int]]:
    """
    Build independent Holding Register and Input Register maps.

    Registers without register_type default to Holding Registers to preserve
    compatibility with existing device definitions.
    """

    hr_map: dict[int, int] = {}
    ir_map: dict[int, int] = {}

    defaults = config.get("encoding", {})
    default_byteorder = defaults.get("byteorder", "big")
    default_wordorder = defaults.get("wordorder", "big")

    for reg in config.get("registers", []):
        address = int(reg["address"])

        values = encode_value(
            register_type=reg["type"],
            value=reg["value"],
            byteorder=reg.get("byteorder", default_byteorder),
            wordorder=reg.get("wordorder", default_wordorder),
        )

        register_space = str(
            reg.get("register_type", "holding")
        ).lower()

        if register_space in {"input", "ir"}:
            target_map = ir_map
        elif register_space in {"holding", "hr"}:
            target_map = hr_map
        else:
            raise ValueError(
                f"Unsupported register_type '{register_space}' "
                f"for register {reg.get('name', address)}"
            )

        for offset, word in enumerate(values):
            target_map[address + offset] = word

    return hr_map, ir_map


def build_full_register_array(block_map: dict[int, int]) -> list[int]:
    values = [0] * 65536

    for address, value in block_map.items():
        if 0 <= address < 65536:
            values[address] = value
        else:
            logger.warning(
                "Ignoring out-of-range register address: %s",
                address,
            )

    return values