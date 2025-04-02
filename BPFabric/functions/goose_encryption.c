#include <linux/if_ether.h>
#include "ebpf_switch.h"

/*
Function which sends GOOSE messages from physical ports to the encryption / decryption stack via a virtual port. 
*/

struct bpf_map_def SEC("maps") inports = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = 6, // MAC address is the key
    .value_size = sizeof(uint32_t),
    .max_entries = 256,
};

uint64_t prog(struct packet *pkt)
{
    uint32_t *original_port;

    //First virtual port is only for traffic uNF -> GEDSF 
    if (pkt->metadata.in_port == 0)
    {
        return DROP;
    }

    //Traffic from physical ports and only GOOSE traffic 
    if (pkt->metadata.in_port >= 2 && pkt->eth.h_proto == 47240) 
    {
        //Learn initial port
        bpf_map_update_elem(&inports, pkt->eth.h_source, &pkt->metadata.in_port, 0);

        return PORT;  // Forwards traffic to virtual port 0 to GEDSF
        //PORT + 1  
        //bpf_mirror(0, pkt, pkt->metadata.length); // Virtual port      
        //return DROP; 
    }

    // Traffic from GEDSF -> uNF
    if (pkt->metadata.in_port == 1 && bpf_map_lookup_elem(&inports, pkt->eth.h_source, &original_port) != -1)
    {
        pkt->metadata.in_port = *original_port;
        return NEXT;
    }

    return DROP;
}
char _license[] SEC("license") = "GPL";
