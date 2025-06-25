#include <linux/if_ether.h>
#include <netinet/ip.h>
#include <netinet/tcp.h>
#include "ebpf_switch.h"

/*
Function which sends MODBUS traffic from physical ports to the non-eBPF stack via a virtual port. 
Requires forwarding at the next stage. 
*/

#include <linux/if_ether.h>
#include "ebpf_switch.h"

struct bpf_map_def SEC("maps") inports = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = 6, // MAC address is the key
    .value_size = sizeof(uint32_t),
    .max_entries = 256,
};

uint64_t prog(struct packet *pkt)
{
    uint32_t *original_port;

    // No traffic from veth1
    if (pkt->metadata.in_port == 0)
    {
        return DROP;
    }

    // Traffic from veth3, rewrite the in_port and forward to the next stage
    if (pkt->metadata.in_port == 1 && bpf_map_lookup_elem(&inports, pkt->eth.h_source, &original_port) != -1)
    {
        pkt->metadata.in_port = *original_port;
        return NEXT;
    }

    // Otherwise learn the original port for this MAC address
    bpf_map_update_elem(&inports, pkt->eth.h_source, &pkt->metadata.in_port, 0);

    // Send MODBUS traffic to the veth1
    
    // Check if the ethernet frame contains an ipv4 payload
    if (pkt->eth.h_proto == 0x0008)
    {
        struct ip *ipv4 = (struct ip *)(((uint8_t *)&pkt->eth) + ETH_HLEN);
    
        // Check if the ip packet contains a TCP payload
        if (ipv4->ip_p == 6)
        {
            struct tcphdr *tcp = (struct tcphdr *)(((uint32_t *)ipv4) + ipv4->ip_hl);
            if(tcp->source == 62977 || tcp->dest == 62977) //corresponds to 502
            {
                return PORT + 0;
            }else
            {
                //Send other traffic to the next stage
                return NEXT; 
            }
        }
    }
    return NEXT; 
}
char _license[] SEC("license") = "GPL";
