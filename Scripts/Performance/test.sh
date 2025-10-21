#!/bin/bash
# Automated switch performance test using iperf3
# Run this on the CLIENT side. Make sure iperf3 server is running on the target host.

SERVER_IP="192.168.1.10"   # <-- change this to your iperf3 server IP
BANDWIDTH="1G"             # target bandwidth
DURATION=10                # test duration in seconds
LOGFILE="iperf_results.log"

# List of packet sizes to test (payload bytes)
PACKET_SIZES=(64 128 256 512 1024 1472 9000)

echo "Starting iperf3 switch performance test..."
echo "Server: $SERVER_IP  |  Bandwidth: $BANDWIDTH  |  Duration: ${DURATION}s"
echo "-------------------------------------------------------------"
echo "Size(Bytes)  Throughput(Mbps)  Loss(%)  Jitter(ms)" > summary.txt

# Empty previous log
> "$LOGFILE"

# Run tests for each packet size
for SIZE in "${PACKET_SIZES[@]}"; do
    echo
    echo ">>> Testing with packet size $SIZE bytes..."
    OUTPUT=$(iperf3 -c $SERVER_IP -u -b $BANDWIDTH -l $SIZE -t $DURATION -J 2>/dev/null)
    echo "$OUTPUT" >> "$LOGFILE"

    # Extract key values from JSON output
    BITRATE=$(echo "$OUTPUT" | jq '.end.sum.bits_per_second' | awk '{printf "%.1f", $1/1000000}')
    LOSS=$(echo "$OUTPUT" | jq '.end.sum.lost_percent')
    JITTER=$(echo "$OUTPUT" | jq '.end.sum.jitter_ms')

    # Handle missing data gracefully
    if [ -z "$BITRATE" ] || [ "$BITRATE" = "null" ]; then BITRATE="0"; fi
    if [ -z "$LOSS" ] || [ "$LOSS" = "null" ]; then LOSS="0"; fi
    if [ -z "$JITTER" ] || [ "$JITTER" = "null" ]; then JITTER="0"; fi

    printf "%-12s %-18s %-9s %-10s\n" "$SIZE" "$BITRATE" "$LOSS" "$JITTER" | tee -a summary.txt
done

echo
echo "-------------------------------------------------------------"
echo "✅ Test completed. Results saved to summary.txt and $LOGFILE"
echo "-------------------------------------------------------------"
cat summary.txt
