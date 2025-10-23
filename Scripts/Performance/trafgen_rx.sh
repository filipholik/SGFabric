#!/bin/bash
# trafgen_rx.sh
# Receiver-side script for L2 switch performance test
# Usage: ./trafgen_rx.sh <iface> <duration> <size>

IFACE=$1
DURATION=$2
SIZE=$3

if [ -z "$IFACE" ] || [ -z "$DURATION" ] || [ -z "$SIZE" ]; then
  echo "Usage: $0 <iface> <duration> <frame_size>"
  exit 1
fi

get_rx() {
    ethtool -S "$IFACE" 2>/dev/null | grep -m1 "rx_packets" | awk '{print $2}'
}

RX_START=$(get_rx)
sleep "$DURATION"
RX_END=$(get_rx)

if [ -z "$RX_START" ] || [ -z "$RX_END" ]; then
    echo "ERROR: Could not read RX counters from $IFACE"
    exit 1
fi

RX_DIFF=$((RX_END - RX_START))
RX_PPS=$(echo "scale=2; $RX_DIFF / $DURATION" | bc)
BITS_PER_FRAME=$(echo "($SIZE + 20) * 8" | bc)   # add IFG+preamble overhead
RX_MBPS=$(echo "scale=2; $RX_PPS * $BITS_PER_FRAME / 1000000" | bc)

echo "$RX_PPS $RX_MBPS"
