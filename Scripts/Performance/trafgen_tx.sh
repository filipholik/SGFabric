#!/bin/bash
# trafgen_tx.sh
# Sender/controller script for L2 switch throughput test

H2_HOST="10.0.0.2"             # IP of H2 (must be reachable via SSH)
H2_IFACE="eth1"                # Interface on H2 receiving traffic
IFACE_TX="eth1"                # Interface on H1 transmitting traffic
DST_MAC="00:11:22:33:44:55"    # Destination MAC (port toward H2)
SRC_MAC="00:aa:bb:cc:dd:ee"    # Source MAC (H1)
DURATION=10                    # Seconds per test
PACKET_SIZES=(64 128 256 512 1024 1518)
LOGFILE="switch_test_results.txt"

echo "=== L2 Switch Throughput Test ==="
echo "TX interface: $IFACE_TX"
echo "RX interface (H2): $H2_IFACE at $H2_HOST"
echo "Test duration: ${DURATION}s per size"
echo "--------------------------------------------------------------"
printf "%-8s %-15s %-15s %-10s %-10s %-8s\n" "Size" "TX_PPS" "RX_PPS" "TX_Mbps" "RX_Mbps" "Loss(%)" > "$LOGFILE"

get_tx() {
    ethtool -S "$IFACE_TX" 2>/dev/null | grep -m1 "tx_packets" | awk '{print $2}'
}

make_template() {
    local size=$1
    local payload_len=$((size - 14))
    cat <<EOF > tmp_${size}.trafgen
{
  $DST_MAC,
  $SRC_MAC,
  0x08,0x00,
  fill($payload_len, 0x00)
}
EOF
}

for SIZE in "${PACKET_SIZES[@]}"; do
    echo
    echo ">>> Testing frame size: $SIZE bytes..."

    make_template "$SIZE"

    TX_START=$(get_tx)
    ssh "$H2_HOST" "./switch_rx_logger.sh $H2_IFACE $DURATION $SIZE" &
    RX_PID=$!

    sudo timeout "$DURATION" trafgen -i "$IFACE_TX" -c tmp_${SIZE}.trafgen --gap 0 >/dev/null 2>&1

    TX_END=$(get_tx)
    RX_OUTPUT=$(wait $RX_PID 2>/dev/null; ssh "$H2_HOST" "cat /tmp/rx_output_${SIZE}.txt" 2>/dev/null)

    TX_DIFF=$((TX_END - TX_START))
    TX_PPS=$(echo "scale=2; $TX_DIFF / $DURATION" | bc)
    BITS_PER_FRAME=$(echo "($SIZE + 20) * 8" | bc)
    TX_MBPS=$(echo "scale=2; $TX_PPS * $BITS_PER_FRAME / 1000000" | bc)

    # Get RX stats directly from H2 script
    RX_STATS=$(ssh "$H2_HOST" "./switch_rx_logger.sh $H2_IFACE $DURATION $SIZE")
    RX_PPS=$(echo "$RX_STATS" | awk '{print $1}')
    RX_MBPS=$(echo "$RX_STATS" | awk '{print $2}')

    # Compute loss percentage
    LOSS=$(echo "scale=2; (1 - $RX_PPS / $TX_PPS) * 100" | bc 2>/dev/null)
    if [[ "$LOSS" == *"nan"* ]]; then LOSS="0.00"; fi

    printf "%-8s %-15s %-15s %-10s %-10s %-8s\n" "$SIZE" "$TX_PPS" "$RX_PPS" "$TX_MBPS" "$RX_MBPS" "$LOSS" | tee -a "$LOGFILE"
done

echo
echo "✅ Test complete! Results saved to $LOGFILE"
echo "--------------------------------------------------------------"
