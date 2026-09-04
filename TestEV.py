from pymodbus.client import ModbusTcpClient

c = ModbusTcpClient("10.255.28.76", port=502)
c.connect()

for addr, count in [
    (1, 1),
    (2, 2),
    (4, 2),
    (101, 1),
    (102, 2),
    (9000, 2),
    (9002, 2),
    (9004, 2),
    (9006, 2),
]:
    r = c.read_input_registers(address=addr, count=count, slave=255)
    print(addr, r.registers if not r.isError() else r)

c.close()