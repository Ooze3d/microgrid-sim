import logging
from typing import Any

from app.core.encoding import encode_value

logger = logging.getLogger("device_server")


def build_block_map(config: dict[str, Any]) -> dict[int, int]:
    block_map: dict[int, int] = {}

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

        for offset, word in enumerate(values):
            block_map[address + offset] = word

    return block_map


def build_full_register_array(block_map: dict[int, int]) -> list[int]:
    values = [0] * 65536

    for address, value in block_map.items():
        if 0 <= address < 65536:
            values[address] = value
        else:
            logger.warning("Ignoring out-of-range register address: %s", address)

    return values