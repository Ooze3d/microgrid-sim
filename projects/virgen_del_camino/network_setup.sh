#!/usr/bin/env bash
set -e

IFACE="eth0"

echo "=== Switching simulator network to Virgen del Camino ==="

# -------------------------------------------------------------------
# 1. Remove known CEN simulator aliases
# -------------------------------------------------------------------

CEN_SIM_IPS=(
  "192.168.52.8/24"
  "192.168.52.32/24"
  "192.168.52.33/24"
  "192.168.52.34/24"
  "192.168.52.35/24"
  "192.168.52.69/24"
  "192.168.52.70/24"
)

echo
echo "Removing CEN simulator IPs..."

for ip in "${CEN_SIM_IPS[@]}"; do
  if ip addr show dev "$IFACE" | grep -q "${ip%/*}"; then
    echo "  removing $ip"
    sudo ip addr del "$ip" dev "$IFACE" || true
  fi
done


# -------------------------------------------------------------------
# 2. Add Virgen del Camino simulator aliases
# -------------------------------------------------------------------

VDC_SIM_IPS=(
  "10.255.28.74/27"   # Sonnen BESS 1
  "10.255.28.75/27"   # Sonnen BESS 2
  "10.255.28.76/27"   # EV charger 1
  "10.255.28.77/27"   # EV charger 2
  "10.255.28.78/27"   # EMA / Web Service Platform
  "10.255.28.79/27"   # PM5563
  "10.255.28.81/27"   # Growatt datalogger
)

echo
echo "Adding Virgen del Camino simulator IPs..."

for ip in "${VDC_SIM_IPS[@]}"; do
  if ip addr show dev "$IFACE" | grep -q "${ip%/*}"; then
    echo "  already present: $ip"
  else
    echo "  adding $ip"
    sudo ip addr add "$ip" dev "$IFACE"
  fi
done


# -------------------------------------------------------------------
# 3. Show resulting interface
# -------------------------------------------------------------------

echo
echo "=== Current IPv4 addresses on $IFACE ==="
ip -4 addr show dev "$IFACE"

echo
echo "Virgen del Camino simulator network ready."