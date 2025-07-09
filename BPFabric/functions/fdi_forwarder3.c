#include <linux/if_ether.h>
#include <netinet/ip.h>
#include <netinet/tcp.h>
#include "ebpf_switch.h"

/*
Function which sends MODBUS traffic from physical ports to the non-eBPF stack via a virtual port. 
Uses static mapping based on port numbers (physical, virtual and TCP) 
*/

volatile const __u32 TCP_SOURCE = 57075 //1505 //502 Little Endian modbus port
//volatile const __u32 TCP_DEST = 10000; 

uint64_t prog(struct packet *pkt)
{
    // No traffic from veth1
    if (pkt->metadata.in_port == 0)
    {
        return DROP;
    }
    
    // Check if the ethernet frame contains an ipv4 payload
    if (pkt->eth.h_proto == 0x0008)
    {
        struct ip *ipv4 = (struct ip *)(((uint8_t *)&pkt->eth) + ETH_HLEN);
    
        // Check if the ip packet contains a TCP payload
        if (ipv4->ip_p == 6)
        {
            struct tcphdr *tcp = (struct tcphdr *)(((uint32_t *)ipv4) + ipv4->ip_hl);
            //Received on physical ports -> virtual
            if(pkt->metadata.in_port == 2 || pkt->metadata.in_port == 3){ 
                return PORT + 0; 
            }            
            //Received from virtual, originating from SOURCE 
            if(tcp->source == TCP_SOURCE && pkt->metadata.in_port == 1){ 
                return PORT + 2; 
            }
            //Received from virtual, originating from DESTINATION 
            if(tcp->dest == TCP_SOURCE && pkt->metadata.in_port == 1){ 
                return PORT + 3; 
            }
        }
    }else{
        //Other traffic, route accordingly 
        if (pkt->metadata.in_port == 2)
        {
            return PORT + 3;
        }
        if (pkt->metadata.in_port == 3)
        {
            return PORT + 2;
        }
    }
    //Should not happen
    return NEXT; 
}
char _license[] SEC("license") = "GPL";