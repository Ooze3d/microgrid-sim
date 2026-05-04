# Microgrid simulator V1

Starter project for a very small lab simulator:
- 1 topological incomer breaker (NSX)
- 1 grid power meter (PM8240 / PM8000-style map as seen by the PLC)

## Run

```bash
docker compose up --build
```

## Endpoints

- Breaker: localhost:15032
- PM Grid: localhost:15034

## Notes

- This first version is intentionally read-focused.
- Register addresses in the YAML files are the PLC-facing addresses you shared.
- If the PLC reads one register off, adjust only the YAML addresses, not the Python code.
- The PM float word order is configurable in YAML (`byteorder`, `wordorder`).
