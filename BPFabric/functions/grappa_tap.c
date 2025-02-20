#include <linux/if_ether.h>
#include "ebpf_switch.h"

uint64_t prog(struct packet *pkt, unsigned len)
{
    if (pkt->metadata.in_port == 1) //enp1s0
    {
        //Check the BPFabric interfaces mapping (index on start)  
        bpf_mirror(0, pkt, len); // def: 2, 100         
    }
  
    return NEXT;
}
char _license[] SEC("license") = "GPL";
