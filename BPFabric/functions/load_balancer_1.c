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

    __u8 h3[ETH_ALEN] = {0x00, 0x00, 0x00, 0x00, 0x00, 0x03};
    __u8 h4[ETH_ALEN] = {0x00, 0x00, 0x00, 0x00, 0x00, 0x04};

    if (pkt->metadata.in_port == 3)
    {
        bpf_notify(2, 0, 0);
        return 1; 
    }
    if (pkt->metadata.in_port == 2)
    {
        bpf_notify(2, 0, 0);
        return 0; 
    }

    /*if (pkt->eth.h_source[5] == h3[5] || pkt->eth.h_source[5] == h4[5])  {
            bpf_notify(2, 0, 0);
            return 1; 
    }    */

    /*if(__builtin_memcmp(pkt->eth.h_source, h3, ETH_ALEN) == 0) //== "000000000003"
    {
        bpf_notify(2, 0, 0);
        return 1; 
    }

    if(__builtin_memcmp(pkt->eth.h_source, h4, ETH_ALEN) == 0) 
    {
        bpf_notify(2, 0, 0);
        return 1; 
    }   */
        
    return NEXT;
}
char _license[] SEC("license") = "GPL";
