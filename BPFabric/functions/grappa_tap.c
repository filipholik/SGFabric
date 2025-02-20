#include <linux/if_ether.h>
#include "ebpf_switch.h"

uint64_t prog(struct packet *pkt, unsigned len)
{
    //Just in case any data from the virtual port
    if (pkt->metadata.in_port == 0)
    {
        return DROP;
    }
    //if (pkt->metadata.in_port == 1) //enp1s0
    //{
        //Check the BPFabric interfaces mapping (index on start)  
    bpf_mirror(0, pkt, len); // Mirror from all the ports        
    //}
  
    return NEXT;
}
char _license[] SEC("license") = "GPL";
