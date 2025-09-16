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

echo
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
spin $sleep_pid "Testing the /read API 1. "
wait $sleep_pid
curl -X POST "http://127.0.0.1:5000/read" \
  -H "Content-Type: application/json" \
  -d '{"dpid": "1", "index": "0", "name": "monitor"}'

echo
sleep 5 & sleep_pid=$!
spin $sleep_pid "Testing the /read API 2. "
wait $sleep_pid
curl -X POST "http://127.0.0.1:5000/read" \
  -H "Content-Type: application/json" \
  -d '{"dpid": "1", "index": "0", "name": "monitor"}'

echo
sleep 5 & sleep_pid=$!
spin $sleep_pid "Testing the /read API 3. "
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

echo
sleep 5 & sleep_pid=$!
spin $sleep_pid "Testing the /status API"
wait $sleep_pid
curl -X GET "http://127.0.0.1:5000/status"

echo
echo "Testing finished" 