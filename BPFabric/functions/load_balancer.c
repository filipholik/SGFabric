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

    if (pkt->eth.h_source[5] == h3[5] || pkt->eth.h_source[5] == h4[5] || 
            pkt->eth.h_dest[5] == h3[5] || pkt->eth.h_dest[5] == h4[5]){
        return 2;
    }else{
        return 1;
    }
}
char _license[] SEC("license") = "GPL";
