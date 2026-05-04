import argparse
import logging
import struct
from pathlib import Path
from typing import Any

import yaml
from pymodbus.datastore import ModbusServerContext, ModbusSlaveContext, ModbusSequentialDataBlock
from pymodbus.server import StartTcpServer

_LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
logger = logging.getLogger("device_server")


def load_yaml(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def swap_words(words: list[int]) -> list[int]:
    if len(words) % 2 != 0:
        raise ValueError("Word swap requires an even number of 16-bit words")
    out: list[int] = []
    for i in range(0, len(words), 2):
        out.extend([words[i + 1], words[i]])
    return out


def encode_value(register_type: str, value: Any, byteorder: str = "big", wordorder: str = "big") -> list[int]:
    rt = register_type.lower()
    bo = byteorder.lower()
    wo = wordorder.lower()

    if rt in {"uint16", "word"}:
        return [int(value) & 0xFFFF]
    if rt == "int16":
        return [struct.unpack(">H" if bo == "big" else "<H", struct.pack(">h" if bo == "big" else "<h", int(value)))[0]]
    if rt == "float32":
        packed = struct.pack(">f" if bo == "big" else "<f", float(value))
        words = list(struct.unpack(">HH" if bo == "big" else "<HH", packed))
        return swap_words(words) if wo == "little" else words
    if rt == "uint32":
        packed = struct.pack(">I" if bo == "big" else "<I", int(value))
        words = list(struct.unpack(">HH" if bo == "big" else "<HH", packed))
        return swap_words(words) if wo == "little" else words
    if rt == "int32":
        packed = struct.pack(">i" if bo == "big" else "<i", int(value))
        words = list(struct.unpack(">HH" if bo == "big" else "<HH", packed))
        return swap_words(words) if wo == "little" else words
    raise ValueError(f"Unsupported register type: {register_type}")


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


def build_context(config: dict[str, Any]) -> ModbusServerContext:
    block_map = build_block_map(config)

    # Full 0-filled Modbus map so the PLC does not get IllegalAddress
    # when it reads auxiliary registers we have not explicitly modeled yet.
    hr_values = [0] * 65536
    ir_values = [0] * 65536

    for address, value in block_map.items():
        if 0 <= address < 65536:
            hr_values[address] = value
            ir_values[address] = value
        else:
            logger.warning("Ignoring out-of-range register address: %s", address)

    slave = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [0] * 65536),
        co=ModbusSequentialDataBlock(0, [0] * 65536),
        hr=ModbusSequentialDataBlock(0, hr_values),
        ir=ModbusSequentialDataBlock(0, ir_values),
        zero_mode=False,
    )

    return ModbusServerContext(slaves=slave, single=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one virtual Modbus TCP device")
    parser.add_argument("--config", required=True, help="Path to YAML device config")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format=_LOG_FORMAT)

    config_path = Path(args.config)
    config = load_yaml(str(config_path))
    device = config["device"]

    context = build_context(config)
    identity = None

    logger.info(
        "Starting %s on %s:%s (unit_id=%s)",
        device["name"],
        device.get("bind", "0.0.0.0"),
        device["port"],
        device.get("unit_id", 255),
    )
    logger.info("Loaded %s configured registers", len(config.get("registers", [])))

    StartTcpServer(
        context=context,
        identity=identity,
        address=(device.get("bind", "0.0.0.0"), int(device["port"])),
    )


if __name__ == "__main__":
    main()
