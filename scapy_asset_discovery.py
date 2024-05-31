#! /usr/bin/env python
from scapy.all import *
from datetime import datetime

GOOSE_PROTOCOL = 0x88B8
INTERFACE = "DPSHMI-eth0"

packet_count = 0 
bytes_count = 0 

def packet_callback(packet): 
     global packet_count
     global bytes_count

     if Ether in packet and packet[Ether].type == GOOSE_PROTOCOL:
          packet_count += 1

          timestamp_capture = packet.time
          timestamp_ns = time.time_ns()
          current_time = datetime.fromtimestamp(timestamp_ns / 1e9)
          current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S") + f'.{timestamp_ns % 1_000_000_000:09d}'
          print(f"New GOOSE received at {current_time_str}: {packet.summary()}")

sniff(prn=packet_callback, iface=INTERFACE, filter="ether proto 0x88B8", store=0)
