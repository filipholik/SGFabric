#!/bin/bash
# Automated switch performance test using iperf3
# Run this on the CLIENT side. Make sure iperf3 server is running on the target host.

SERVER_IP="10.0.0.1"
BANDWIDTH="2.5G"
DURATION=60
LOGFILE="iperf_results.log"
#PACKET_SIZES=(64 128 256 512 1024 1472) #1472 9000
PACKET_SIZES=(64)
# Parameter -w 512k to increase socket buffer

echo "Starting iperf3 switch performance test..."
echo "Server: $SERVER_IP | Bandwidth: $BANDWIDTH | Duration: ${DURATION}s"
echo "-------------------------------------------------------------"
echo "Size(Bytes)  Throughput(Mbps)  Loss(%)  Jitter(ms)" > summary.txt
> "$LOGFILE"

for SIZE in "${PACKET_SIZES[@]}"; do
    echo
    echo ">>> Testing with packet size $SIZE bytes..."
    
    OUTPUT=$(iperf3 -c "$SERVER_IP" -u -b "$BANDWIDTH" -l "$SIZE" -t "$DURATION" -w 2M -P 12 -J 2>/dev/null)
    if [ -z "$OUTPUT" ]; then
        echo "WARNING: No output from iperf3 - check server or connection" | tee -a summary.txt
        continue
    fi

    # Validate success field
    SUCCESS=$(echo "$OUTPUT" | jq -r '.error // empty')
    if [ -n "$SUCCESS" ]; then
        echo "WARNING: iPerf3 error: $SUCCESS" | tee -a summary.txt
        continue
    fi

    BITRATE=$(echo "$OUTPUT" | jq '.end.sum.bits_per_second' | awk '{printf "%.1f", $1/1000000}')
    LOSS=$(echo "$OUTPUT" | jq '.end.sum.lost_percent')
    JITTER=$(echo "$OUTPUT" | jq '.end.sum.jitter_ms')

    # Handle null or empty values
    if [ -z "$BITRATE" ] || [ "$BITRATE" = "null" ]; then BITRATE="0"; fi
    if [ -z "$LOSS" ] || [ "$LOSS" = "null" ]; then LOSS="0"; fi
    if [ -z "$JITTER" ] || [ "$JITTER" = "null" ]; then JITTER="0"; fi

    printf "%-12s %-18s %-9s %-10s\n" "$SIZE" "$BITRATE" "$LOSS" "$JITTER" | tee -a summary.txt
done

echo
echo "-------------------------------------------------------------"
echo "INFO: Test completed. Results saved to summary.txt and $LOGFILE"
echo "-------------------------------------------------------------"
cat summary.txt
