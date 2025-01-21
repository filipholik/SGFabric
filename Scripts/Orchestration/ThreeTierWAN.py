#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call
import time 

from eBPFSwitch import eBPFSwitch, eBPFHost

def smartGridSimNetwork():

    net = Mininet( topo=None,
                   build=False,
                   ipBase='1.0.0.0/8',
                   host = eBPFHost, 
                   switch = eBPFSwitch)

    info( '\n*** ************************************* *** \n' )
    info( '*** Starting Three Tier WAN Model Topology *** \n' )    
    info( '*** Version: 250121 \n' )
    info( '*** Author: filip.holik@glasgow.ac.uk  \n' )
    info( '*** ************************************* *** \n' )
    #info( '*** Adding controller\n' )
    #c0=net.addController(name='c0',
    #                  controller=OVSController,
    #                  protocol='tcp',
    #                  port=6633)

    switchPath = "../../BPFabric/softswitch/softswitch"; 

    switchType = OVSKernelSwitch; 

    info( '*** Starting networking devices\n')
    C1 = net.addSwitch('C1', switch_path=switchPath, dpid=1)    
    C2 = net.addSwitch('C2', switch_path=switchPath, dpid=2)    
    D1 = net.addSwitch('D1', switch_path=switchPath, dpid=3)
    D2 = net.addSwitch('D2', switch_path=switchPath, dpid=4) 
    D3 = net.addSwitch('D3', switch_path=switchPath, dpid=5) 
    D4 = net.addSwitch('D4', switch_path=switchPath, dpid=6) 
    A1 = net.addSwitch('A1', switch_path=switchPath, dpid=7) 
    A2 = net.addSwitch('A2', switch_path=switchPath, dpid=8) 
    A3 = net.addSwitch('A3', switch_path=switchPath, dpid=9) 
    A4 = net.addSwitch('A4', switch_path=switchPath, dpid=10) 
    D5 = net.addSwitch('D5', switch_path=switchPath, dpid=11) 
    A5 = net.addSwitch('A5', switch_path=switchPath, dpid=12) 
    W1 = net.addSwitch('W1', switch_path=switchPath, dpid=12) 
    W2 = net.addSwitch('W2', switch_path=switchPath, dpid=12) 

    info( '*** Starting hosts \n')
    H1 = net.addHost('H1', cls=eBPFHost, ip='10.0.0.1', defaultRoute='10.10.10.10',mac='00:00:00:00:00:01')
    H2 = net.addHost('H2', cls=eBPFHost, ip='10.0.0.2', defaultRoute='10.10.10.10',mac='00:00:00:00:00:02')
    H3 = net.addHost('H3', cls=eBPFHost, ip='10.0.0.3', defaultRoute='10.10.10.10',mac='00:00:00:00:00:03')
    H4 = net.addHost('H4', cls=eBPFHost, ip='10.0.0.4', defaultRoute='10.10.10.10',mac='00:00:00:00:00:04')
    H5 = net.addHost('H5', cls=eBPFHost, ip='10.0.0.5', defaultRoute='10.10.10.10',mac='00:00:00:00:00:05')
    H6 = net.addHost('H6', cls=eBPFHost, ip='10.0.0.6', defaultRoute='10.10.10.10',mac='00:00:00:00:00:06')
    H7 = net.addHost('H7', cls=eBPFHost, ip='10.0.0.7', defaultRoute='10.10.10.10',mac='00:00:00:00:00:07')
    H8 = net.addHost('H8', cls=eBPFHost, ip='10.0.0.8', defaultRoute='10.10.10.10',mac='00:00:00:00:00:08')
    SERVER = net.addHost('SERVER', cls=eBPFHost, ip='10.10.10.10', defaultRoute='10.10.10.10',mac='00:00:00:00:00:10')

    info( '*** Setting link parameters\n')
    #WAN1 = {'bw':1000,'delay':'20ms','loss':1,'jitter':'10ms'} 
    #GBPS = {'delay':'18ms'} 
    MBPS = {'bw':1} 
    MBPS10 = {'bw':2.5}
    MBPS100 = {'bw':10}

    info( '*** Adding links\n')
    net.addLink(H1, A1, cls=TCLink , **MBPS)
    net.addLink(H2, A1, cls=TCLink , **MBPS)
    net.addLink(H3, A2, cls=TCLink , **MBPS)
    net.addLink(H4, A2, cls=TCLink , **MBPS)
    net.addLink(A1, D1, cls=TCLink , **MBPS10)
    net.addLink(A2, D2, cls=TCLink , **MBPS10)
    net.addLink(D1, C1, cls=TCLink , **MBPS10)
    net.addLink(D2, C1, cls=TCLink , **MBPS10)
    
    net.addLink(H5, A3, cls=TCLink , **MBPS)
    net.addLink(H6, A3, cls=TCLink , **MBPS)
    net.addLink(H7, A4, cls=TCLink , **MBPS)
    net.addLink(H8, A4, cls=TCLink , **MBPS)
    net.addLink(A3, D3, cls=TCLink , **MBPS10)
    net.addLink(A4, D4, cls=TCLink , **MBPS10)
    net.addLink(D3, C2, cls=TCLink , **MBPS10)
    net.addLink(D4, C2, cls=TCLink , **MBPS10)

    #net.addLink(C1, C2, cls=TCLink , **MBPS100)
    net.addLink(C2, D5, cls=TCLink , **MBPS100)
    net.addLink(D5, A5, cls=TCLink , **MBPS100)
    net.addLink(A5, SERVER, cls=TCLink , **MBPS100)

    net.addLink(C1, W1, cls=TCLink , **MBPS10)
    net.addLink(C1, W2, cls=TCLink , **MBPS10)
    net.addLink(W1, C2, cls=TCLink , **MBPS10)
    net.addLink(W2, C2, cls=TCLink , **MBPS10)

    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting networking devices\n')
    net.get('C1').start([])
    net.get('C2').start([])
    net.get('D1').start([])
    net.get('D2').start([])
    net.get('D3').start([])
    net.get('D4').start([])
    net.get('A1').start([])
    net.get('A2').start([])
    net.get('A3').start([])
    net.get('A4').start([])
    net.get('D5').start([])
    net.get('A5').start([])
    net.get('W1').start([])
    net.get('W2').start([])

    info( '*** Preparing custom scripts \n')
    CLI.do_orch_measure = orch_measure
    CLI.do_orch_rtt_1 = orch_rtt_1
    CLI.do_orch_rtt_2 = orch_rtt_2
    CLI.do_orch_attack_ddos = orch_attack_ddos
    CLI.do_orch_attack_dos = orch_attack_dos
    info( '*** Three Tier WAN Topology Started *** \n' )
    CLI(net)
    net.stop()

def orch_attack_ddos(self, line):
    "Starts the DDoS attack to the server." 
    net = self.mn  
    info('Starting DDoS attack... \n')    
    net.get('H1').cmdPrint('xterm -geometry 90x30+10+10 -fa "Monospace" -fs 12 -T "H1-DDOS" -e "sudo hping3 -S --flood 10.10.10.10;bash"&') 
    net.get('H2').cmdPrint('xterm -geometry 90x30+10+10 -fa "Monospace" -fs 12 -T "H2-DDOS" -e "sudo hping3 -S --flood 10.10.10.10;bash"&') 
    net.get('H4').cmdPrint('xterm -geometry 90x30+10+10 -fa "Monospace" -fs 12 -T "H4-DDOS" -e "sudo hping3 -S --flood 10.10.10.10;bash"&') 
    net.get('H6').cmdPrint('xterm -geometry 90x30+10+10 -fa "Monospace" -fs 12 -T "H6-DDOS" -e "sudo hping3 -S --flood 10.10.10.10;bash"&') 
    net.get('H7').cmdPrint('xterm -geometry 90x30+10+10 -fa "Monospace" -fs 12 -T "H7-DDOS" -e "sudo hping3 -S --flood 10.10.10.10;bash"&') 

def orch_attack_dos(self, line):
    "Starts the DoS attack to the server." 
    net = self.mn  
    info('Starting DoS attack... \n')    
    net.get('H1').cmdPrint('xterm -geometry 90x30+10+10 -fa "Monospace" -fs 12 -T "H1-DDOS" -e "sudo hping3 -S --flood 10.10.10.10;bash"&') 

def orch_measure(self, line):
    "Starts throughput measurement." 
    net = self.mn  
    info('Starting throughput measurement... \n')    
    net.get('SERVER').cmdPrint('xterm -geometry 90x30+10+10 -fa "Monospace" -fs 12 -T "SERVER-Service" -e "iperf -s;bash"&') 
    time.sleep(1)
    net.get('H3').cmdPrint('xterm -geometry 90x30+10+10 -fa "Monospace" -fs 12 -T "H3-Client" -e "iperf -c 10.10.10.10;bash"&') 

def orch_rtt_1(self, line):
    "Starts RTT measurement." 
    net = self.mn  
    info('Starting RTT measurement 1... \n')   
    net.get('H1').cmdPrint('xterm -geometry 90x30+10+10 -fa "Monospace" -fs 12 -T "H1-Client" -e "ping -s 6400 -i 0.1 10.10.10.10;bash"&') 
    net.get('H2').cmdPrint('xterm -geometry 90x30+10+10 -fa "Monospace" -fs 12 -T "H2-Client" -e "ping -s 6400 -i 0.1 10.10.10.10;bash"&')      
    #net.get('H3').cmdPrint('xterm -geometry 90x30+10+10 -fa "Monospace" -fs 12 -T "H3-Client" -e "ping -s 6400 -i 0.1 10.10.10.10;bash"&') 
    #net.get('H4').cmdPrint('xterm -geometry 90x30+10+10 -fa "Monospace" -fs 12 -T "H4-Client" -e "ping -s 6400 -i 0.1 10.10.10.10;bash"&') 

def orch_rtt_2(self, line):
    "Starts RTT measurement." 
    net = self.mn  
    info('Starting RTT measurement 2... \n')   
    #net.get('H1').cmdPrint('xterm -geometry 90x30+10+10 -fa "Monospace" -fs 12 -T "H1-Client" -e "ping -s 6400 -i 0.1 10.10.10.10;bash"&') 
    #net.get('H2').cmdPrint('xterm -geometry 90x30+10+10 -fa "Monospace" -fs 12 -T "H2-Client" -e "ping -s 6400 -i 0.1 10.10.10.10;bash"&')      
    net.get('H3').cmdPrint('xterm -geometry 90x30+10+10 -fa "Monospace" -fs 12 -T "H3-Client" -e "ping -s 6400 -i 0.1 10.10.10.10;bash"&') 
    net.get('H4').cmdPrint('xterm -geometry 90x30+10+10 -fa "Monospace" -fs 12 -T "H4-Client" -e "ping -s 6400 -i 0.1 10.10.10.10;bash"&') 

if __name__ == '__main__':
    setLogLevel( 'info' )
    smartGridSimNetwork()





