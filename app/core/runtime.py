import logging
from typing import Any

from pymodbus.datastore import (
    ModbusServerContext,
    ModbusSlaveContext,
    ModbusSequentialDataBlock,
)

from app.core.datablock import InteractiveDataBlock
from app.core.model_factory import create_model
from app.core.register_map import build_block_map, build_full_register_array

logger = logging.getLogger("device_server")


def build_context(config: dict[str, Any]) -> tuple[ModbusServerContext, ModbusSlaveContext, object]:
    block_map = build_block_map(config)

    hr_values = build_full_register_array(block_map)
    ir_values = build_full_register_array(block_map)

    model = create_model(config)

    slave = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [0] * 65536),
        co=ModbusSequentialDataBlock(0, [0] * 65536),
        hr=InteractiveDataBlock(0, hr_values, model),
        ir=ModbusSequentialDataBlock(0, ir_values),
        zero_mode=False,
    )

    context = ModbusServerContext(slaves=slave, single=True)

    return context, slave, model