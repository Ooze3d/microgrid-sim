# Microgrid Simulator – Modular Device Architecture

## Overview

This project started as a simple Modbus TCP virtual device simulator intended to emulate a single Schneider NSX breaker. During development and integration with a real Schneider Electric microgrid PLC/HMI architecture (Machine Expert + Vijeo/EOTE), the project evolved into a much broader concept:

> A reusable modular simulation framework capable of emulating complete microgrid architectures composed of heterogeneous industrial devices.

The simulator is designed to:

- Emulate real Modbus TCP industrial devices.
- Provide realistic operational behaviour.
- Simulate interactions between devices.
- Validate PLC logic before field commissioning.
- Reduce time spent debugging in customer installations.
- Allow fast replication of different architectures.
- Support future expansion to BESS, PCS, PV inverters, dataloggers and complete power systems.

---

# Core Philosophy

The most important architectural decision introduced in this version is the separation between:

1. Device Type
2. Device Instance
3. Device Behaviour
4. Device Interaction Triggers
5. System Architecture

This separation allows the simulator to scale from:

- 1 virtual breaker

To:

- Complete microgrid simulations with dozens of devices.

Without duplicating logic.

---

# New Modular Structure

## Device Types

A device type defines:

- Modbus register map
- Supported commands
- Internal behaviour
- Dynamic logic
- State transitions

Example:

```text
app/device_types/nsx_legacy/
    default_registers.yaml
    model.py
```

Other future device types:

```text
app/device_types/
    pm8000/
    sungrow_pv/
    sinexcel_pcs/
    narada_bms/
```

---

## Device Instances

A device instance defines:

- Device name
- IP address
- Unit ID
- Behaviour parameters
- PLC interaction triggers
- Project-specific overrides

Example:

```text
configs/breaker_sotano.yaml
```

The same device type can therefore be instantiated multiple times:

```text
breaker_sotano
breaker_hvac
breaker_taller
breaker_lighting
```

All sharing the same NSX behaviour model.

---

# Trigger Philosophy (Key Concept)

## Initial Problem

During integration testing, the simulator successfully emulated:

- Modbus reads
- Status feedback
- Electrical values

However:

- The PLC did not visibly transmit the expected Modbus FC16 write commands to the simulator.

Despite this:

- Real breakers opened correctly in the field.
- The PLC internally reflected the requested operations.

This led to an important realization.

---

# The Eureka Moment

The HMI and PLC already exchange command intentions internally.

Example:

```text
HMI requests breaker open
↓
PLC internal register changes
↓
PLC logic processes request
↓
Physical device eventually changes state
```

The simulator does not necessarily need to receive the final physical Modbus write command.

Instead:

> The simulator can react to the PLC command intention itself.

This became the foundation of the new trigger architecture.

---

# Trigger-Based Device Interaction

Each device model can define command triggers.

Example:

```yaml
command:
  plc_triggers:
    open:
      address: 11060
      bit: 0
      value: 1

    close:
      address: 11060
      bit: 1
      value: 1
```

Meaning:

```text
If PLC register 11060 bit 0 becomes 1:
→ Simulate breaker opening.
```

This architecture allows the simulator to:

- React to HMI commands.
- React to PLC logic.
- Validate system behaviour.
- Test islanding.
- Test load shedding.
- Test EMS/PMS behaviour.

Without requiring the final field communication path to be fully replicated.

---

# Why This Approach Matters

This trigger-based architecture solves several real-world commissioning problems.

## Advantages

### 1. Fast Functional Validation

The goal of precommissioning is not perfect hardware replication.

The goal is:

```text
"Does the system logic behave correctly?"
```

The trigger system validates exactly that.

---

### 2. Decoupling from Vendor-Specific Complexity

Some industrial devices:

- Use proprietary command layers.
- Use hidden Modbus command interfaces.
- Use internal gateway logic.
- Use communication paths difficult to replicate.

The trigger approach avoids blocking the simulation project on these details.

---

### 3. Scalable Architecture

Each command becomes:

```text
Trigger → Behaviour → Register Update
```

This is easy to scale.

Even complex devices such as PCS systems remain manageable because:

- The number of possible commands is finite.
- Each command simply maps to behaviour.

---

### 4. Realistic Simulation

The simulator can evolve later into:

```text
Trigger validation
+ interlocks
+ delays
+ communication faults
+ protection logic
+ physical dependencies
+ dynamic power flow
```

Without redesigning the architecture.

---

# Device Runtime Philosophy

Each device runs its own behavioural model.

Example:

```text
NSX breaker:
- open
- close
- reset
- dynamic currents
- dynamic power values
```

Example future PCS:

```text
PCS:
- grid mode
- island mode
- power setpoint
- ramp rate
- fault state
- startup sequence
```

The runtime periodically updates:

- Registers
- Internal states
- Dynamic measurements
- Device interactions

---

# Configuration Merge System

The simulator now merges:

```text
Device Type Defaults
+
Device Instance Configuration
```

Example:

```text
nsx_legacy/default_registers.yaml
+
breaker_sotano.yaml
```

This avoids:

- Giant duplicated YAML files.
- Copy/paste register maps.
- Configuration drift.

---

# Long-Term Goal

The long-term objective is:

> Build complete virtual microgrid architectures capable of validating real PLC projects before field commissioning.

Future capabilities may include:

- Virtual buses
- Power flow simulation
- Island transitions
- BESS charge/discharge logic
- PV curtailment
- Frequency response
- Black start sequences
- Dynamic load profiles
- Communication loss scenarios
- Protection simulations

---

# Current Status

Implemented:

- Modular architecture
- Device type separation
- Device instance configuration
- Dynamic NSX model
- Trigger-based command execution
- Runtime loop
- Modular datastore interaction
- Config merge system

In progress:

- PLC register trigger integration
- Interactive breaker behaviour
- Island mode validation
- Dynamic load simulation

Planned:

- PM8000 model
- PCS Sinexcel model
- Narada BMS model
- Architecture-level interactions
- Virtual power flow engine

---

# Final Philosophy

This simulator is not intended to be:

```text
A simple fake Modbus responder.
```

It is intended to become:

```text
A modular digital twin framework for industrial microgrid systems.
```

The trigger architecture introduced in this version is the key concept that makes this scalable and practical for real engineering wo