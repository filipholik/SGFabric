#include <linux/if_ether.h>
#include <linux/ip.h>
#include <linux/icmp.h>
#include "ebpf_switch.h"

struct bpf_map_def SEC("maps") blacklist = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = 6, // MAC address is the key
    .value_size = 16, // Throughput 
    .max_entries = 1024,
};


uint64_t prog(struct packet *pkt)
{
    //__u8 attacker_0[ETH_ALEN] = {0x00, 0x00, 0x00, 0x00, 0x00, 0x03};
    __u16 *throughput; 

    if (bpf_map_lookup_elem(&blacklist, pkt->eth.h_source, &throughput) == -1)
    {              
        return NEXT;
    }else   
    {        
        return DROP;
    }    
}
char _license[] SEC("license") = "GPL";
