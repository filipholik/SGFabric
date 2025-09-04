# !/bin/bash
# Script for testing of the northbound API of the IOL broker of the COCOON Programmable Node (CPN) 
# University of Glasgow, 2025 

echo "Testing the /status API"
curl -X GET "http://127.0.0.1:5000/status"

echo
echo "Testing the /install API"
curl -X POST "http://127.0.0.1:5000/install" \
  -H "Content-Type: application/json" \
  -d '{"dpid": "1", "index": "1", "function_name": "forwarding"}'