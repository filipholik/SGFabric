#include <linux/if_ether.h>
#include "ebpf_switch.h"

/*
Function which sends GOOSE messages from physical ports to the encryption / decryption stack via a virtual port. 
*/

uint64_t prog(struct packet *pkt)
{
    if (pkt->metadata.in_port != 0 && pkt->eth.h_proto == 47240) //Physical ports
    {
        return PORT; //PORT + 1  
        //bpf_mirror(0, pkt, pkt->metadata.length); // Virtual port      
        //return DROP; 
    }
  
    return NEXT;
}
char _license[] SEC("license") = "GPL";
