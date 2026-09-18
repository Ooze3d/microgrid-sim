# Microgrid Simulator TODO

## Core
- [ ] Replace internal holding-register writes with set_internal_values() in all models
- [ ] Add tests/checks for internal-vs-external write separation

## PCS Danfoss
- [x] Logical state -> Modbus status/mode
- [ ] Observe PLC writes to 1159 / 1530 / 1532
- [ ] Implement START/STOP behaviour
- [ ] Implement RESET behaviour
- [ ] Implement CSI/VSI transitions
- [ ] Review exact Danfoss control-word semantics

## Electrical model
- [ ] Add grid_available
- [ ] Add grid_connected
- [ ] Add bus_powered
- [ ] Decouple upstream PM voltage from breaker state

## Scenario layer
- [ ] Runtime external-condition state
- [ ] grid_loss scenario
- [ ] PCS/BMS fault injection