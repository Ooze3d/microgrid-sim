import struct
from typing import Any


def swap_words(words: list[int]) -> list[int]:
    if len(words) % 2 != 0:
        raise ValueError("Word swap requires an even number of 16-bit words")

    out: list[int] = []
    for i in range(0, len(words), 2):
        out.extend([words[i + 1], words[i]])

    return out


def encode_value(
    register_type: str,
    value: Any,
    byteorder: str = "big",
    wordorder: str = "big",
) -> list[int]:
    rt = register_type.lower()
    bo = byteorder.lower()
    wo = wordorder.lower()

    if rt in {"uint16", "word"}:
        return [int(value) & 0xFFFF]

    if rt == "int16":
        return [
            struct.unpack(
                ">H" if bo == "big" else "<H",
                struct.pack(">h" if bo == "big" else "<h", int(value)),
            )[0]
        ]

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