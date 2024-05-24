#!/usr/bin/env python

from core import eBPFCoreApplication, set_event_handler, FLOOD
from core.packets import *

from threading import Thread
from twisted.internet import reactor

from flask import Flask, request, jsonify
import json 
import time

import datetime

app = Flask(__name__)
#global eBPFApp

class storage():
    connected_devices = set()
    connections = {}
    status = {"status" : "Unknown"}
    cache = {}
    log = {} 
    eBPFApp = None

class eBPFCLIApplication(eBPFCoreApplication):
    """
        Controller application that will start a interactive CLI.
    """
    #assetDiscoveryCache = tablesCache() 

    def run(self):        
        Thread(target=reactor.run, kwargs={'installSignalHandlers': 0}).start()
        #return self

    @set_event_handler(Header.TABLES_LIST_REPLY)
    def tables_list_reply(self, connection, pkt):
        #tabulate([ (e.table_name, TableDefinition.TableType.Name(e.table_type), e.key_size, e.value_size, e.max_entries) for e in pkt.entries ], headers=['name', 'type', 'key size', 'value size', 'max entries'])
        print()

    @set_event_handler(Header.TABLE_LIST_REPLY)
    def table_list_reply(self, connection, pkt):
        if pkt.entry.table_name == "assetdisc":
            self.asset_disc_list(connection.dpid, pkt) # Collecting data for Asset Discovery service 
            return 
    
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

        #tabulate(entries, headers=["Key", "Value"])

    @set_event_handler(Header.TABLE_ENTRY_GET_REPLY)
    def table_entry_get_reply(self, connection, pkt):
        #tabulate([(pkt.key.hex(), pkt.value.hex())], headers=["Key", "Value"])
        print()

    def asset_disc_list(self, dpid, pkt):
        os.system('clear')
        entries = []
        
        item_size = pkt.entry.key_size + pkt.entry.value_size
        fmt = "{}s{}s".format(pkt.entry.key_size, pkt.entry.value_size)

        for i in range(pkt.n_items):
            key, value = struct.unpack_from(fmt, pkt.items, i * item_size)
            entries.append((key.hex(), value.hex()))        

        self.assetDiscoveryCache.tablesDict[""] = entries 
        print("Table logged")
        #tabulate(entries, headers=["Key", "Value"])

        headers = {
            'Content-Type': 'application/json'            
        }

        payload = {
            'name': 'John Doe',
            'email': 'john.doe@example.com'
        }

        response = requests.post('http://127.0.0.1:5000/tab', headers=headers, data=json.dumps(entries)) 
        print(response.json())

    #@app.get("/install")
    #def install_functions():    
        #eBPFApp.install()
        #return '<h2> Installing functions to the nodes... <br/> <a href="http://localhost:5085/index"> Back </a> </h2>'
        #return json.dumps(list(storage.connected_devices))
    
    def install(self): 
        log = ""
        print(f'Installing SGSim orchestration functions...')
        log += f'Installing SGSim orchestration functions...' 
        if(len(self.application.connections) == 9): 
            print(f'All networking device connected. ')
            log += f'All networking device connected. '
            with open('../examples/learningswitch.o', 'rb') as f:
                print("Installing forwarding services...")
                elf = f.read() # Otherwise if read 9x - not enough data for ELF header error
                self.application.connections[1].send(FunctionAddRequest(name="learningswitch", index=1, elf=elf)) # DSS1                
                self.application.connections[2].send(FunctionAddRequest(name="learningswitch", index=1, elf=elf)) # DSS2
                self.application.connections[3].send(FunctionAddRequest(name="learningswitch", index=0, elf=elf)) # C
                self.application.connections[4].send(FunctionAddRequest(name="learningswitch", index=0, elf=elf)) # C
                self.application.connections[5].send(FunctionAddRequest(name="learningswitch", index=0, elf=elf)) # C
                self.application.connections[6].send(FunctionAddRequest(name="learningswitch", index=1, elf=elf)) # DPSGW
                self.application.connections[7].send(FunctionAddRequest(name="learningswitch", index=2, elf=elf)) # DPSRS
                self.application.connections[8].send(FunctionAddRequest(name="learningswitch", index=1, elf=elf)) # DPSHV
                self.application.connections[9].send(FunctionAddRequest(name="learningswitch", index=1, elf=elf)) # DPSMV
                time.sleep(1)    
                print("All forwarding services installed...")            

            with open('../examples/mirror.o', 'rb') as f:
                print("Installing mirroring service...")
                elf = f.read() 
                self.application.connections[1].send(FunctionAddRequest(name="mirror", index=0, elf=elf)) # DSS1                
                time.sleep(1)
                print("Mirroring service installed...")

            with open('../examples/block.o', 'rb') as f:
                print("Installing ACL service...")
                elf = f.read() 
                self.application.connections[6].send(FunctionAddRequest(name="acl", index=0, elf=elf))                 
                time.sleep(1)
                print("ACL service installed...")                

            with open('../examples/assetdisc.o', 'rb') as f:
                print("Installing Asset Discovery service...")
                elf = f.read() 
                self.application.connections[7].send(FunctionAddRequest(name="assetdisc", index=0, elf=elf))   
                self.application.connections[8].send(FunctionAddRequest(name="assetdisc", index=0, elf=elf))
                self.application.connections[9].send(FunctionAddRequest(name="assetdisc", index=0, elf=elf))
                self.application.connections[2].send(FunctionAddRequest(name="assetdisc", index=0, elf=elf))             
                time.sleep(1)
                print("ACL service installed...")              

            time.sleep(1)
            print("All functions installed...")
            storage.status["functions"] = ("Functions installed")
        else: 
            print(f'Could not verify connected devices. ')
            storage.status["functions"] = ("Functions not installed")
        
        storage.log[str(datetime.datetime.now())] = log 

    @set_event_handler(Header.NOTIFY)
    def notify_event(self, connection, pkt):        
        #print(f'\n[{connection.dpid}] Received notify event {pkt.id}, data length {pkt.data}')
        #print(pkt.data.hex())
        vendor = ''
        if pkt.data.hex() == '30b216000004':
            vendor = 'Hitachi'
        if pkt.data.hex() == 'b4b15a000001':
            vendor = 'Siemens'  
        #print(f'\n[{eBPFCLIApplication.get_switch_name(connection.dpid)}] IED device detected with MAC: {pkt.data.hex()} ({vendor})')
        connection.send(TableListRequest(index=0, table_name="assetdisc"))


    @set_event_handler(Header.PACKET_IN)
    def packet_in(self, connection, pkt):
        print(f"\n[{connection.dpid}] Received packet in {pkt.data.hex()}")

    @set_event_handler(Header.FUNCTION_LIST_REPLY)
    def function_list_reply(self, connection, pkt):
        #tabulate([ (e.index or 0, e.name, e.counter or 0) for e in pkt.entries ], headers=['index', 'name', 'counter'])
        print()

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


    def get_switch_name(dpid): 
        switch_name = ""; 
        match dpid: 
            case 1: 
                switch_name = "DSS1 GW"
            case 2: 
                switch_name = "DSS2 GW"
            case 3: 
                switch_name = "WAN R1"
            case 4: 
                switch_name = "WAN R2"
            case 5: 
                switch_name = "CONTROL SW"
            case 6: 
                switch_name = "DPS GW"
            case 7: 
                switch_name = "DPS RS"
            case 8: 
                switch_name = "DPS HV"
            case 9: 
                switch_name = "DPS MV"
            case _:
                switch_name = "unknown"   
        return switch_name

@app.get("/start")
def start():
    #Thread(target=reactor.run, kwargs={'installSignalHandlers': 0}).start()
    storage.eBPFApp = eBPFCLIApplication().run()
    storage.status["status"] = "Nodes connected"
    return '<h2> Connecting to the nodes... <br/> <a href="http://localhost:5085/index"> Back </a> </h2>'

@app.get("/status")
def get_status():    
    print(storage.log)
    return json.dumps({"connected_devices" : list(storage.connected_devices), 
                       "log" : storage.log
                       })
    #return len(storage.connected_devices)
    #return {"Connected devices: ": len(storage.connected_devices)}
    #return storage.status 

@app.get("/ad")
def refresh_asset_discovery():    
    return json.dumps(list(storage.connected_devices))

@app.get("/install")
def install_functions():    
    #storage.eBPFApp.install()
    install()
    return '<h2> Installing functions to the nodes... <br/> <a href="http://localhost:5085/index"> Back </a> </h2>'
    #return json.dumps(list(storage.connected_devices))

def install(): 
    print(f'Installing SGSim orchestration functions...')
    if(len(storage.connected_devices) == 9): 
        print(f'All networking device connected. ')
        with open('../examples/learningswitch.o', 'rb') as f:
            print("Installing forwarding services...")
            elf = f.read() # Otherwise if read 9x - not enough data for ELF header error
            storage.connections[1].send(FunctionAddRequest(name="learningswitch", index=1, elf=elf)) # DSS1                
            storage.connections[2].send(FunctionAddRequest(name="learningswitch", index=1, elf=elf)) # DSS2
            storage.connections[3].send(FunctionAddRequest(name="learningswitch", index=0, elf=elf)) # C
            storage.connections[4].send(FunctionAddRequest(name="learningswitch", index=0, elf=elf)) # C
            storage.connections[5].send(FunctionAddRequest(name="learningswitch", index=0, elf=elf)) # C
            storage.connections[6].send(FunctionAddRequest(name="learningswitch", index=1, elf=elf)) # DPSGW
            storage.connections[7].send(FunctionAddRequest(name="learningswitch", index=2, elf=elf)) # DPSRS
            storage.connections[8].send(FunctionAddRequest(name="learningswitch", index=1, elf=elf)) # DPSHV
            storage.connections[9].send(FunctionAddRequest(name="learningswitch", index=1, elf=elf)) # DPSMV
            time.sleep(1)    
            print("All forwarding services installed...")   
            # return         

        with open('../examples/mirror.o', 'rb') as f:
            print("Installing mirroring service...")
            elf = f.read() 
            storage.connections[1].send(FunctionAddRequest(name="mirror", index=0, elf=elf)) # DSS1                
            time.sleep(1)
            print("Mirroring service installed...")

        with open('../examples/block.o', 'rb') as f:
            print("Installing ACL service...")
            elf = f.read() 
            storage.connections[6].send(FunctionAddRequest(name="acl", index=0, elf=elf))                 
            time.sleep(1)
            print("ACL service installed...")                

        with open('../examples/assetdisc.o', 'rb') as f:
            print("Installing Asset Discovery service...")
            elf = f.read() 
            storage.connections[7].send(FunctionAddRequest(name="assetdisc", index=0, elf=elf))   
            storage.connections[8].send(FunctionAddRequest(name="assetdisc", index=0, elf=elf))
            storage.connections[9].send(FunctionAddRequest(name="assetdisc", index=0, elf=elf))
            storage.connections[2].send(FunctionAddRequest(name="assetdisc", index=0, elf=elf))             
            time.sleep(1)
            print("ACL service installed...")              

        time.sleep(1)
        print("All functions installed...")
        storage.status["functions"] = ("Functions installed")
    else: 
        print(f'Could not verify connected devices. ')
        storage.status["functions"] = ("Functions not installed")

#class LearningSwitchApplication(eBPFCoreApplication):
    #@set_event_handler(Header.HELLO)
    #def hello(self, connection, pkt):
        #self.mac_to_port = {}

        #with open('../examples/learningswitch.o', 'rb') as f:
            #print("Installing the eBPF ELF")
            #connection.send(FunctionAddRequest(name="learningswitch", index=0, elf=f.read()))

if __name__ == '__main__':
    #LearningSwitchApplication().run()
    app.run(host="172.17.0.1", port=5000)
    
