#!/usr/bin/env python

from core import eBPFCoreApplication, set_event_handler, FLOOD
from core.packets import *
import struct

from threading import Thread
from twisted.internet import reactor

from flask import Flask, request, jsonify
import json 
import time

import datetime
from enum import Enum

app = Flask(__name__)
#global eBPFApp

DDOS_MITIGATION_THRESHOLD = 1000000 # 1000000 = 1Mbps

class storage():
    connected_devices = set()
    connections = {}
    status = {"status" : "Unknown"}
    cache = {}
    log = {str(datetime.datetime.now()): "Orchestrator started"}
    asset_discovery = {} # dpid: mac : bytes : packets
    monitoring = {} # mac : bytes
    eBPFApp = None

class NF(Enum): 
    FORWARDING = 1
    MIRRORING = 2
    ACL = 3
    ASSET_DISCOVERY = 4
    DOS_MITIGATION = 5
    MONITORING = 6
    GOOSE_ANALYSER = 7

class testingFrontEnd():
    devicesPipelines = {
        1 : [NF.MIRRORING.value, NF.FORWARDING.value], # DSS1
        2 : [NF.ASSET_DISCOVERY.value, NF.FORWARDING.value],  # DSS2
        3 : [NF.FORWARDING.value],  # C
        4 : [NF.FORWARDING.value],  # C
        5 : [NF.FORWARDING.value],  # C
        6 : [NF.MONITORING.value, NF.ACL.value, NF.FORWARDING.value],  # DPSGW
        7 : [NF.GOOSE_ANALYSER.value, NF.ASSET_DISCOVERY.value, NF.FORWARDING.value],  # DPSRS
        8 : [NF.ASSET_DISCOVERY.value, NF.FORWARDING.value],  # DPSHV
        9 : [NF.ASSET_DISCOVERY.value, NF.FORWARDING.value]  # DPSGW
    }
# TODO - specify indexes for NFs


class eBPFCLIApplication(eBPFCoreApplication):
    """
        Service broker for the controller that provides an abstraction between the application and data plane layers. 
    """
    #assetDiscoveryCache = tablesCache() 

    def run(self):        
        Thread(target=reactor.run, kwargs={'installSignalHandlers': 0}).start()
        #return self

    def get_switch_name(dpid): 
        switch_name = ""; 
        match dpid: 
            case 1: 
                switch_name = "C1"
            case 2: 
                switch_name = "C2"
            case 3: 
                switch_name = "D1"
            case 4: 
                switch_name = "D2"
            case 5: 
                switch_name = "D3"
            case 6: 
                switch_name = "D4"
            case 7: 
                switch_name = "A1"
            case 8: 
                switch_name = "A2"
            case 9: 
                switch_name = "A3"
            case 10: 
                switch_name = "A4"
            case _:
                switch_name = "unknown"   
        return switch_name
    
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
        #print("Table reply received: " + str(connection) + "," + str(pkt))
        if pkt.entry.table_name == "assetdisc":
            self.asset_disc_list(connection.dpid, pkt) # Collecting data for Asset Discovery service 
            return 
        
        if pkt.entry.table_name == "monitor":
            self.monitoring_list(connection.dpid, pkt) # Collecting data for Monitoring service 
            return 
        
        if pkt.entry.table_name == "goose_analyser":
            self.goose_analyser_list(connection.dpid, pkt) # Collecting data for GOOSE Analyser
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

    @set_event_handler(Header.TABLE_ENTRY_INSERT_REPLY)
    def table_entry_get_reply(self, connection, pkt):
        print("Table insert reply received: " + str(pkt))

    @set_event_handler(Header.TABLE_ENTRY_GET_REPLY)
    def table_entry_get_reply(self, connection, pkt):
        #tabulate([(pkt.key.hex(), pkt.value.hex())], headers=["Key", "Value"])
        print()

    def monitoring_list(self, dpid, pkt):
        entries = {}
        packets = {}

        #f = open("monitoring_logg.txt", "a")      

        timestamp = str(datetime.datetime.now())        
        #f.write(str(timestamp) + "\n")
        
        item_size = pkt.entry.key_size + pkt.entry.value_size
        fmt = "{}s{}s".format(pkt.entry.key_size, pkt.entry.value_size)

        for i in range(pkt.n_items):
            key, value = struct.unpack_from(fmt, pkt.items, i * item_size)
            #entries.append((key.hex(), value.hex()))   
            valStr = eBPFCLIApplication.get_str_values(value)
            bytesTotal = valStr.split(",",1)[1]
            if key not in storage.monitoring: 
                storage.monitoring[key] = 0 
            
            bandwidth = int(bytesTotal) - int(storage.monitoring[key])
            storage.monitoring[key] = int(bytesTotal)

            bandwidth *= 8; #Bytes to bits 
            if ((bandwidth > DDOS_MITIGATION_THRESHOLD) and (str(key.hex()) != "000000000010")): # Server MAC 000000000010
                self.mitigate_ddos(key, bandwidth)

            if bandwidth > 0: 
                #f.write(str(timestamp) + ";" + str(key.hex()) + ";" + str(bandwidth) + "\n")
                print(str(timestamp) + ";" + str(key.hex()) + ";" + str(bandwidth) + "\n")


            #entries = {str(key.hex()) : eBPFCLIApplication.get_str_values(value)} # str(value.hex()
            #packets[i] = entries
            #storage.asset_discovery[str(key.hex())] = str(value.hex())    
            
        #storage.asset_discovery[eBPFCLIApplication.get_switch_name(dpid)] = packets
        #f.write(packets)
        #f.write(str("--- \n"))
        #f.close()
        #print("Monitoring logged")

    def mitigate_ddos(self, eth_src, value): 
        throughputMbps = value/1000000; 
        print("Mitigating DDoS against: " + str(eth_src.hex()) + " with throughput: " + str(round(throughputMbps,2)) + "Mbps")
        #print(eth_src)
        #print(int.to_bytes(int(round(throughputMbps,0))))
        #storage.connections[1].send(TableEntryInsertRequest(table_name="blacklist", key=eth_src, value=int.to_bytes(int(round(throughputMbps,0))))) # 
        #storage.connections[2].send(TableEntryInsertRequest(table_name="blacklist", key=eth_src, value=int.to_bytes(int(round(throughputMbps,0))))) # 
        #storage.connections[3].send(TableEntryInsertRequest(table_name="blacklist", key=eth_src, value=int.to_bytes(int(round(throughputMbps,0))))) # 
        #storage.connections[4].send(TableEntryInsertRequest(table_name="blacklist", key=eth_src, value=int.to_bytes(int(round(throughputMbps,0))))) # 
        #storage.connections[5].send(TableEntryInsertRequest(table_name="blacklist", key=eth_src, value=int.to_bytes(int(round(throughputMbps,0))))) # 
        #storage.connections[6].send(TableEntryInsertRequest(table_name="blacklist", key=eth_src, value=int.to_bytes(int(round(throughputMbps,0))))) # D4
        storage.connections[7].send(TableEntryInsertRequest(table_name="blacklist", key=eth_src, value=int.to_bytes(int(round(throughputMbps,0))))) # A1
        storage.connections[8].send(TableEntryInsertRequest(table_name="blacklist", key=eth_src, value=int.to_bytes(int(round(throughputMbps,0))))) # A2
        storage.connections[9].send(TableEntryInsertRequest(table_name="blacklist", key=eth_src, value=int.to_bytes(int(round(throughputMbps,0))))) # A3
        storage.connections[10].send(TableEntryInsertRequest(table_name="blacklist", key=eth_src, value=int.to_bytes(int(round(throughputMbps,0))))) # A4
        #storage.connections[11].send(TableEntryInsertRequest(table_name="blacklist", key=eth_src, value=int.to_bytes(int(round(throughputMbps,0))))) # D6
        #storage.connections[12].send(TableEntryInsertRequest(table_name="blacklist", key=eth_src, value=int.to_bytes(int(round(throughputMbps,0))))) # A5

    def goose_analyser_list(self, dpid, pkt):
        #os.system('clear')
        #entries = []
        entries = {}
        packets = {}
        
        item_size = pkt.entry.key_size + pkt.entry.value_size
        fmt = "{}s{}s".format(pkt.entry.key_size, pkt.entry.value_size)

        print("GOOSE Analyser")
        for i in range(pkt.n_items):
            key, value = struct.unpack_from(fmt, pkt.items, i * item_size)
            #entries.append((key.hex(), value.hex()))   
            entries = {str(key.hex()) : eBPFCLIApplication.get_str_values(value)} # str(value.hex()
            packets[i] = entries
            print(eBPFCLIApplication.get_switch_name(dpid) + ": " + str(key.hex()) + ", stNum: " + (str(value.hex()))[:8] + ", sqNum: " + (str(value.hex()))[-8:]) 
            #storage.asset_discovery[str(key.hex())] = str(value.hex())    
            
        #storage.asset_discovery[eBPFCLIApplication.get_switch_name(dpid)] = packets
        #print(eBPFCLIApplication.get_switch_name(dpid) + ": " + str(key.hex()) + ", " + str(value.hex())) 
        #self.assetDiscoveryCache.tablesDict[""] = entries 
        #print("GAN: " + str(packets))


    def asset_disc_list(self, dpid, pkt):
        #os.system('clear')
        #entries = []
        entries = {}
        packets = {}
        
        item_size = pkt.entry.key_size + pkt.entry.value_size
        fmt = "{}s{}s".format(pkt.entry.key_size, pkt.entry.value_size)

        for i in range(pkt.n_items):
            key, value = struct.unpack_from(fmt, pkt.items, i * item_size)
            #entries.append((key.hex(), value.hex()))   
            entries = {str(key.hex()) : eBPFCLIApplication.get_str_values(value)} # str(value.hex()
            packets[i] = entries
            #storage.asset_discovery[str(key.hex())] = str(value.hex())    
            
        storage.asset_discovery[eBPFCLIApplication.get_switch_name(dpid)] = packets
        #print(eBPFCLIApplication.get_switch_name(dpid) + ": " + str(key.hex()) + ", " + str(value.hex())) 
        #self.assetDiscoveryCache.tablesDict[""] = entries 
        #print("Table logged")
        #tabulate(entries, headers=["Key", "Value"])
 
    @set_event_handler(Header.NOTIFY)
    def notify_event(self, connection, pkt):    
        return    
        print(f'\n[{connection.dpid}] Received notify event {pkt.id}, data length {pkt.data}')
        print(pkt.data.hex())
        
        vendor = ''
        if pkt.data.hex() == '30b216000004':
            vendor = 'Hitachi'
        if pkt.data.hex() == 'b4b15a000001':
            vendor = 'Siemens'  
        #print(f'\n[{eBPFCLIApplication.get_switch_name(connection.dpid)}] IED device detected with MAC: {pkt.data.hex()} ({vendor})')    
        connection.send(TableListRequest(index=0, table_name="assetdisc"))
        connection.send(TableListRequest(index=1, table_name="assetdisc")) # For the DoS service! 
        #connection.send(TableListRequest(index=0, table_name="monitor"))

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

@app.get("/start")
def start():
    #Thread(target=reactor.run, kwargs={'installSignalHandlers': 0}).start()
    storage.eBPFApp = eBPFCLIApplication().run()
    storage.status["status"] = "Nodes connected"    
    #return '<h2> Connecting to the nodes... <br/> <a href="http://127.0.0.1:5000/index"> Back </a> </h2>'
    return loading_bar("Connecting to the nodes... ", 50)


def loading_bar(headline, frames): 
        return """\
        <!DOCTYPE html>
<html>
<style>
#myProgress {
  width: 100%;
  text-align: center;
  background-color: #ddd;
}

#myBar {
  width: 10%;
  height: 30px;
  background-color: #2ed8b6; //#04AA6D;
  text-align: center;
  line-height: 30px;
  color: black;
}

#content{
  background-color: #ddd;
  text-align: center;
  display:none;
}
</style>

<head>
    <script>
    var i = 0;
    function move() {
        if (i == 0) {
            i = 1;
            var elem = document.getElementById("myBar");
            var width = 10;
            var id = setInterval(frame, """ + str(frames) + """);
            function frame() {
                if (width >= 100) {
                    clearInterval(id);
                    document.getElementById('content').style.display = 'block'; 
                    document.getElementById('myProgress').style.display = 'none'; 
                    i = 0;
                } else {
                    width++;
                    elem.style.width = width + "%";
                    elem.innerHTML = width  + "%";
                }
            }
        }
    }
    window.onload = move; 
    </script>
</head>

<body>

<div id="myProgress">
    <h1>""" + headline + """</h1>
    <div id="myBar">10%</div>
</div>

<div id="content">
    <h1>Finished</h1>
    <h1><a href="http://127.0.0.1:5000/index"> Back </a></h1>
</div>

</body>
</html>

"""


@app.get("/status")
def get_status():    
    #print(storage.log)
    return json.dumps({"connected_devices" : list(storage.connected_devices), 
                       "log" : storage.log, 
                       "asset_discovery" : storage.asset_discovery
                       })
    #return len(storage.connected_devices)
    #return {"Connected devices: ": len(storage.connected_devices)}
    #return storage.status 

@app.get("/ad")
def refresh_asset_discovery():    
    return json.dumps(list(storage.connected_devices))

@app.get("/ddosm")
def install_ddosm():    
    installThread = Thread(target=install_ddosm)
    installThread.start()    
    return loading_bar("Installing mitigation functions... ", 10)

@app.get("/install")
def install_functions():    
    #storage.eBPFApp.install()
    installThread = Thread(target=install)
    installThread.start()    
    return loading_bar("Installing functions... ", 100)
    
    #return '<h1> All functions installed... <br/> <a href="http://127.0.0.1:5000/index"> Back </a> </h1>'
    #return json.dumps(list(storage.connected_devices))

def threaded_mon_timer():
    while True:
        storage.connections[11].send(TableListRequest(index=1, table_name="monitor")) #D4 
        #storage.connections[7].send(TableListRequest(index=0, table_name="goose_analyser"))
        #connection.send(TableListRequest(index=0, table_name="assetdisc"))
        #print("Sending monitoring request")
        time.sleep(1)

def start_monitoring():
    thread = Thread(target = threaded_mon_timer, args = ())
    thread.start() 

def install_ddosm():
    with open('../functions/ddos_mitigation.o', 'rb') as f:
            print("Installing Denial of Service Prevention service...")
            elf = f.read() 
            storage.connections[8].send(FunctionAddRequest(name="ddos", index=0, elf=elf)) #0               
            print("Denial of Service Prevention service installed...")  

def install(): 
    print(f'Installing SGSim orchestration functions...')    
    storage.log[str(datetime.datetime.now())] = "Installation of functions started"
    if(len(storage.connected_devices) == 12): 
        print(f'All networking device connected. ')
        with open('../functions/forwarding.o', 'rb') as f:
            print("Installing forwarding services...")
            elf = f.read() # Otherwise if read 9x - not enough data for ELF header error
            storage.connections[1].send(FunctionAddRequest(name="learningswitch", index=2, elf=elf)) # C1                
            storage.connections[2].send(FunctionAddRequest(name="learningswitch", index=2, elf=elf)) # C2
            storage.connections[3].send(FunctionAddRequest(name="learningswitch", index=2, elf=elf)) # D1
            storage.connections[4].send(FunctionAddRequest(name="learningswitch", index=2, elf=elf)) # D2
            storage.connections[5].send(FunctionAddRequest(name="learningswitch", index=2, elf=elf)) # D3
            storage.connections[6].send(FunctionAddRequest(name="learningswitch", index=2, elf=elf)) # D4
            storage.connections[7].send(FunctionAddRequest(name="learningswitch", index=2, elf=elf)) # A1
            storage.connections[8].send(FunctionAddRequest(name="learningswitch", index=2, elf=elf)) # A2
            storage.connections[9].send(FunctionAddRequest(name="learningswitch", index=2, elf=elf)) # A3
            storage.connections[10].send(FunctionAddRequest(name="learningswitch", index=2, elf=elf)) # A4
            storage.connections[11].send(FunctionAddRequest(name="learningswitch", index=2, elf=elf)) # A4
            storage.connections[12].send(FunctionAddRequest(name="learningswitch", index=2, elf=elf)) # A4
            time.sleep(1)    
            print("All forwarding services installed...")   
            # return         

        with open('../functions/mirror.o', 'rb') as f:
            print("Installing mirroring service...")
            elf = f.read() 
            #storage.connections[1].send(FunctionAddRequest(name="mirror", index=0, elf=elf)) # DSS1                
            time.sleep(1)
            print("Mirroring service installed...")

        with open('../functions/block.o', 'rb') as f:
            print("Installing ACL service...")
            elf = f.read() 
            #storage.connections[6].send(FunctionAddRequest(name="acl", index=1, elf=elf))
            #storage.connections[2].send(FunctionAddRequest(name="acl", index=0, elf=elf))                  
            time.sleep(1)
            print("ACL service installed...")                

        with open('../functions/assetdisc.o', 'rb') as f:
            print("Installing Asset Discovery service...")
            elf = f.read() 
            #storage.connections[7].send(FunctionAddRequest(name="assetdisc", index=1, elf=elf))   
            #storage.connections[8].send(FunctionAddRequest(name="assetdisc", index=1, elf=elf)) #0
            #storage.connections[9].send(FunctionAddRequest(name="assetdisc", index=0, elf=elf))
            #storage.connections[2].send(FunctionAddRequest(name="assetdisc", index=0, elf=elf))             
            time.sleep(1)
            print("ACL service installed...")   

        with open('../functions/dos_mitigation.o', 'rb') as f:
            print("Installing Denial of Service Prevention service...")
            elf = f.read() 
            #storage.connections[8].send(FunctionAddRequest(name="dos", index=0, elf=elf)) #0   
            time.sleep(1)
            print("Denial of Service Prevention service installed...")     

        with open('../functions/ddos_auto_mitigation.o', 'rb') as f:
            print("Installing Automated Distributed Denial of Service Mitigation service...")
            elf = f.read()     
            #storage.connections[1].send(FunctionAddRequest(name="blacklist", index=0, elf=elf)) # C1                
            #storage.connections[2].send(FunctionAddRequest(name="blacklist", index=0, elf=elf)) # C2
            #storage.connections[3].send(FunctionAddRequest(name="blacklist", index=0, elf=elf)) # D1
            #storage.connections[4].send(FunctionAddRequest(name="blacklist", index=0, elf=elf)) # D2
            #storage.connections[5].send(FunctionAddRequest(name="blacklist", index=0, elf=elf)) # D3       
            #storage.connections[6].send(FunctionAddRequest(name="blacklist", index=0, elf=elf)) #D4   
            storage.connections[7].send(FunctionAddRequest(name="blacklist", index=0, elf=elf)) #A1 
            storage.connections[8].send(FunctionAddRequest(name="blacklist", index=0, elf=elf)) #A2 
            storage.connections[9].send(FunctionAddRequest(name="blacklist", index=0, elf=elf)) #A3 
            storage.connections[10].send(FunctionAddRequest(name="blacklist", index=0, elf=elf)) #A4 
            #storage.connections[11].send(FunctionAddRequest(name="blacklist", index=0, elf=elf)) #D5 
            #storage.connections[12].send(FunctionAddRequest(name="blacklist", index=0, elf=elf)) #A5 
            time.sleep(1)
            print("Automated Distributed Denial of Service Mitigation service installed...") 

        with open('../functions/monitoring.o', 'rb') as f:
            print("Installing Monitoring service...")
            elf = f.read() 
            storage.connections[11].send(FunctionAddRequest(name="monitor", index=1, elf=elf)) #0   
            #storage.connections[7].send(FunctionAddRequest(name="monitor", index=1, elf=elf)) #0   
            start_monitoring()
            time.sleep(1)
            print("Monitoring service installed...")         

        with open('../functions/goose_analyser.o', 'rb') as f:
            print("Installing GOOSE analyser service...")
            elf = f.read() 
            #storage.connections[7].send(FunctionAddRequest(name="goose_analyser", index=0, elf=elf)) #0   
            time.sleep(1)
            print("GOOSE analyser service installed...")    

        time.sleep(1)
        print("All functions installed...")
        storage.status["functions"] = ("Functions installed")
        storage.log[str(datetime.datetime.now())] = "All functions installed sucessfully"
    else: 
        print(f'Could not verify connected devices. ')
        storage.status["functions"] = ("Functions not installed")
        storage.log[str(datetime.datetime.now())] = "Functions installation failed"

if __name__ == '__main__':
    #LearningSwitchApplication().run()
    #app.run(host="172.17.0.1", port=5000)
    app.run(host="127.0.0.1", port=5050)
    
