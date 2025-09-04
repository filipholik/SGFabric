# !/bin/bash
# Script for testing of the northbound API of the IOL broker of the COCOON Programmable Node (CPN) 
# University of Glasgow, 2025 

#!/bin/bash

spin() {
    local pid=$1
    local message=$2
    local -a marks=('/' '-' '\' '|')
    local i=0
    while kill -0 "$pid" 2>/dev/null; do
        i=$(( (i+1) % 4 ))
        printf "\r%s %s" "$message" "${marks[i]}"
        sleep 0.2
    done
    printf "\r%s Done!    \n" "$message"
}

progress_bar() {
    local duration=$1
    local interval=0.1
    local ticks=0

    # Calculate total ticks using bc for float division
    local total_ticks=$(echo "$duration / $interval" | bc)

    while [ $ticks -le $total_ticks ]; do
        # Calculate percent using bc
        percent=$(echo "scale=0; $ticks * 100 / $total_ticks" | bc)
        filled=$(( percent / 2 ))
        empty=$(( 50 - filled ))

        bar=$(printf "%${filled}s" | tr ' ' '#')
        spaces=$(printf "%${empty}s")

        printf "\r[%s%s] %d%%" "$bar" "$spaces" "$percent"

        sleep $interval
        ticks=$((ticks + 1))
    done
    echo
    #echo -e "\nDone!"
}
echo "Preparing to test the CPN IOL Northbound API" 
progress_bar 5

# echo "Testing the /status API"
sleep 5 & sleep_pid=$!
spin $sleep_pid "Testing the /status API"
wait $sleep_pid
curl -X GET "http://127.0.0.1:5000/status"

echo
sleep 5 & sleep_pid=$!
spin $sleep_pid "Testing the /install API - monitoring function"
wait $sleep_pid
curl -X POST "http://127.0.0.1:5000/install" \
  -H "Content-Type: application/json" \
  -d '{"dpid": "1", "index": "0", "function_name": "monitoring"}'

echo
sleep 5 & sleep_pid=$!
spin $sleep_pid "Testing the /install API - forwarding function"
wait $sleep_pid
curl -X POST "http://127.0.0.1:5000/install" \
  -H "Content-Type: application/json" \
  -d '{"dpid": "1", "index": "1", "function_name": "forwarding"}'

echo
sleep 5 & sleep_pid=$!
spin $sleep_pid "Testing the /read API"
wait $sleep_pid
curl -X POST "http://127.0.0.1:5000/read" \
  -H "Content-Type: application/json" \
  -d '{"dpid": "1", "index": "0", "name": "monitor"}'

echo
sleep 5 & sleep_pid=$!
spin $sleep_pid "Testing the /remove API"
wait $sleep_pid
curl -X POST "http://127.0.0.1:5000/remove" \
  -H "Content-Type: application/json" \
  -d '{"dpid": "1", "index": "0"}'
curl -X POST "http://127.0.0.1:5000/remove" \
  -H "Content-Type: application/json" \
  -d '{"dpid": "1", "index": "1"}'

sleep 5 & sleep_pid=$!
spin $sleep_pid "Testing the /status API"
wait $sleep_pid
curl -X GET "http://127.0.0.1:5000/status"

echo
echo "Testing finished" 