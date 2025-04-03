#include <linux/if_ether.h>
#include "ebpf_switch.h"

/*
Function which sends GOOSE messages from physical ports to the encryption / decryption stack via a virtual port. 
Combines simple forwarding. 
*/

uint64_t prog(struct packet *pkt)
{
    //First virtual port is only for traffic uNF -> GEDSF 
    if (pkt->metadata.in_port == 0)
    {
        return DROP;
    }

    //Traffic from physical ports and only GOOSE traffic 
    if (pkt->metadata.in_port == 2 && pkt->eth.h_proto == 47240) 
    {       
        return PORT;  // Forwards traffic to virtual port 0 to GEDSF
        //PORT + 1  
        //bpf_mirror(0, pkt, pkt->metadata.length); // Virtual port      
        //return DROP; 
    }

    // Traffic from GEDSF -> uNF
    if (pkt->metadata.in_port == 1)
    {
        return PORT + 3; //Forward to physical port 2
    }

    return DROP;
}
char _license[] SEC("license") = "GPL";
