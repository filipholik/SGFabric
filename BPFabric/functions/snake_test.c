#include <linux/if_ether.h>
#include "ebpf_switch.h"

uint64_t prog(struct packet *pkt)
{
    // If the packet is from the IDS (port 0) drop it
    if (pkt->metadata.in_port == 0) 
    {
        return PORT + 1; 
    }    

    if (pkt->metadata.in_port == 2) 
    {
        return PORT + 3; 
    } 

    if (pkt->metadata.in_port == 4) 
    {
        return PORT + 5; 
    } 

    return DROP;
}
char _license[] SEC("license") = "GPL";
