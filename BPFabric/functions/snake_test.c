#include <linux/if_ether.h>
#include "ebpf_switch.h"

uint64_t prog(struct packet *pkt)
{
    // One-way
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

    // Return traffic
    if (pkt->metadata.in_port == 5) 
    {
        return PORT + 4; 
    }    

    if (pkt->metadata.in_port == 3) 
    {
        return PORT + 2; 
    } 

    if (pkt->metadata.in_port == 1) 
    {
        return PORT; 
    } 

    return DROP;
}
char _license[] SEC("license") = "GPL";
