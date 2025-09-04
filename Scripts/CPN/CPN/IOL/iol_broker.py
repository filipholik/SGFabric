#!/usr/bin/env python

from core import eBPFCoreApplication, set_event_handler, FLOOD
from core.packets import *
import struct
import sys

from threading import Thread
from twisted.internet import reactor

from flask import Flask, request, jsonify
import json 
import time

import datetime
from enum import Enum

app = Flask(__name__)
#global CPNControllerApp

class storage():
    connected_devices = set()
    connections = {}
    status = {"status" : "Unknown"}
    log = {str(datetime.datetime.now()): "Broker initialized"}
    monitoring = {} # mac : bytes
    CPNControllerApp = None

class NF(Enum): 
    FORWARDING = 1
    MONITORING = 2 # DEMO

class CPNController(eBPFCoreApplication):
    """
        Service broker for the controller that provides an abstraction between the application and data plane layers. 
    """

    def run(self):        
        Thread(target=reactor.run, kwargs={'installSignalHandlers': 0}).start()
        #return self
    
    def get_str_values(value): 
        #print(int.from_bytes(bytes.fromhex(str(value.hex())[:8]), byteorder="little")) # Bytes 
        #print(int.from_bytes(bytes.fromhex(str(value.hex())[-8:]), byteorder="little")) # Packets 
        value_bytes = int.from_bytes(bytes.fromhex(str(value.hex())[:8]), byteorder="little") 
        value_packets = int.from_bytes(bytes.fromhex(str(value.hex())[-8:]), byteorder="little")
        #print(str(value_packets) + "," + str(value_bytes))
        return str(value_packets) + "," + str(value_bytes)

    @set_event_handler(Header.TABLES_LIST_REPLY)
    def tables_list_reply(self, connection, pkt):
        #tabulate([ (e.table_name, TableDefinition.TableType.Name(e.table_type), e.key_size, e.value_size, e.max_entries) for e in pkt.entries ], headers=['name', 'type', 'key size', 'value size', 'max entries'])
        print()

    @set_event_handler(Header.TABLE_LIST_REPLY)
    def table_list_reply(self, connection, pkt):        
    
        entries = []

        if pkt.entry.table_type in [TableDefinition.HASH, TableDefinition.LPM_TRIE]:
            item_size = pkt.entry.key_size + pkt.entry.value_size
            fmt = "{}s{}s".format(pkt.entry.key_size, pkt.entry.value_size)

            for i in range(pkt.n_items):
                key, value = struct.unpack_from(fmt, pkt.items, i * item_size)
                entries.append((key.hex(), value.hex()))

        elif pkt.entry.table_type == TableDefinition.ARRAY:
            item_size = pkt.entry.value_size
            fmt = "{}s".format(pkt.entry.value_size)

            for i in range(pkt.n_items):
                value = struct.unpack_from(fmt, pkt.items, i * item_size)[0]
                entries.append((i, value.hex()))

        tabulate(entries, headers=["Key", "Value"])

    @set_event_handler(Header.TABLE_ENTRY_GET_REPLY)
    def table_entry_get_reply(self, connection, pkt):
        tabulate([(pkt.key.hex(), pkt.value.hex())], headers=["Key", "Value"])
        print()
 
    @set_event_handler(Header.NOTIFY)
    def notify_event(self, connection, pkt):        
        print(f'\n[{connection.dpid}] Received notify event {pkt.id}, data length {pkt.data}')
        print(pkt.data.hex())        

    @set_event_handler(Header.PACKET_IN)
    def packet_in(self, connection, pkt):
        print(f"\n[{connection.dpid}] Received packet in {pkt.data.hex()}")

    @set_event_handler(Header.FUNCTION_LIST_REPLY)
    def function_list_reply(self, connection, pkt):
        tabulate([ (e.index or 0, e.name, e.counter or 0) for e in pkt.entries ], headers=['index', 'name', 'counter'])
        print()

    def tabulate(rows, headers=None):
        if not rows or len(rows) == 0:
            print('<Empty Table>')
            return

        # Find the largest possible value for each column
        columns_width = [ max([ len(str(row[i])) for row in rows ]) for i in range(len(rows[0])) ]

        # If there are headers check if headers is larger than content
        if headers:
            columns_width = [ max(columns_width[i], len(header)) for i, header in enumerate(headers) ]

        # Add two extra spaces to columns_width for prettiness
        columns_width = [ w+2 for w in columns_width ]

        # Generate the row format string and delimiter string
        row_format = '  '.join(['{{:>{}}}'.format(w) for w in columns_width ])
        row_delim  = [ '='*w for w in columns_width ]

        # Print the headers if necessary
        print('')
        if headers:
            print(row_format.format(*headers))

        # Print the rows
        print(row_format.format(*row_delim))
        for row in rows:
            print(row_format.format(*row))
        print(row_format.format(*row_delim))

    @set_event_handler(Header.FUNCTION_ADD_REPLY)
    def function_add_reply(self, connection, pkt):
        if pkt.status == FunctionAddReply.FunctionAddStatus.INVALID_STAGE:
            print("Cannot add a function at this index")
        elif pkt.status == FunctionAddReply.FunctionAddStatus.INVALID_FUNCTION:
            print("Unable to install this function")
        else:
            print("Function has been installed")

    @set_event_handler(Header.FUNCTION_REMOVE_REPLY)
    def function_remove_reply(self, connection, pkt):
        if pkt.status == FunctionAddReply.FunctionAddStatus.INVALID_STAGE:
            print("Cannot remove a function at this index")
        else:
            print("Function has been removed")

    @set_event_handler(Header.HELLO)
    def hello(self, connection, pkt):
        print(connection) 
        if connection.dpid not in storage.connected_devices: 
            storage.connected_devices.add(connection.dpid)
        storage.connections[connection.dpid] = connection
        storage.log[str(datetime.datetime.now())] = "New node connected: " + str(connection.dpid)
        print("New device connected")

# Northbound REST API

#@app.get("/start")
#def start():
    #Thread(target=reactor.run, kwargs={'installSignalHandlers': 0}).start()
    #storage.CPNControllerApp = CPNController().run()
    #storage.status["status"] = "Nodes connected"    
    #return '<h2> Connecting to the nodes... <br/> <a href="http://127.0.0.1:5000/index"> Back </a> </h2>'
    #return loading_bar("Connecting to the nodes... ", 50)


@app.get("/status")
def get_status():    
    #print(storage.log)
    return json.dumps({"connected_devices" : list(storage.connected_devices), 
                       "status" : storage.status, 
                       "log" : storage.log
                       })
    #return len(storage.connected_devices)
    #return {"Connected devices: ": len(storage.connected_devices)}
    #return storage.status 

@app.get("/ad")
def refresh_asset_discovery():    
    return json.dumps(list(storage.connected_devices))

@app.route('/install', methods=['POST'])
def install_function():    
    try: 
        data = request.get_json()  # Parse raw JSON body
        print(f"Received request: {data}")
        #return jsonify({"status": "success", "data" : data}), 200
        dpid = data.get("dpid")
        index = data.get("index")
        function_name = data.get("function_name")
        print(f"Installation request received, dpid: {dpid}, index: {index}, function_name: {function_name}")
        return install(dpid, index, function_name)
        
    except Exception as e:
        print(f"Error installing the function {e}")
        return jsonify({'error': f'Error installing the function {e}'}), 500

def install(dpid, index, function_name): 
    with open(f'../functions/{function_name}.o', 'rb') as f:
        print(f"Installing {function_name} function...")
        elf = f.read() 
        if(int(dpid) in storage.connections):                         
            storage.connections[int(dpid)].send(FunctionAddRequest(name=function_name, index=int(index), elf=elf))              
            #time.sleep(1)    
            print("Function installed...")                      
            storage.status["functions"] = (f"Function {function_name} installed at index {index} and DPID {dpid}")
            storage.log[str(datetime.datetime.now())] = f"Function {function_name} installed at index {index} and DPID {dpid}"
            return jsonify({"status": "success", "description" : "Function was installed successfully"}), 200
        else:
            return jsonify({"status": "failed", "description" : "No device with this DPID"}), 500
    return jsonify({"status": "failed", "description" : "Cannot read the file"}), 500
            

        

        

if __name__ == '__main__':
    ip = sys.argv[1] 
    port = int(sys.argv[2]) 
    print("Starting up the IOL broker with IP: {} and port: {} ...".format(ip, port))

    #app.run(host="127.0.0.1", port=5000)

    storage.CPNControllerApp = CPNController().run()
    storage.status["status"] = "CPN Controller is running... "
    storage.log[str(datetime.datetime.now())] = "CPN Controller started"

    app.run(host=ip, port=port)

    
    
