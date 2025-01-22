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
    __u8 h1[ETH_ALEN] = {0x00, 0x00, 0x00, 0x00, 0x00, 0x01};
    __u8 h2[ETH_ALEN] = {0x00, 0x00, 0x00, 0x00, 0x00, 0x02};
    __u8 h3[ETH_ALEN] = {0x00, 0x00, 0x00, 0x00, 0x00, 0x03};
    __u8 h4[ETH_ALEN] = {0x00, 0x00, 0x00, 0x00, 0x00, 0x04};
    __u8 h10[ETH_ALEN] = {0x00, 0x00, 0x00, 0x00, 0x00, 0x10};

    //bpf_notify(999, pkt->eth.h_dest, sizeof(pkt->eth.h_dest));

    if ((pkt->eth.h_dest[5] == h3[5] || pkt->eth.h_dest[5] == h4[5]) && pkt->metadata.in_port > 1)  {
            bpf_notify(22, 0, 0);
            return 1; 
    }
    
    /*if(__builtin_memcmp(pkt->eth.h_dest, h3, ETH_ALEN) == 0) //== "000000000003"
    {
        bpf_notify(22, 0, 0);
        return 1; 
    }

    if(__builtin_memcmp(pkt->eth.h_dest, h4, ETH_ALEN) == 0) 
    {
        bpf_notify(22, 0, 0);
        return 1; 
    }*/
        
    return NEXT;
}
char _license[] SEC("license") = "GPL";
