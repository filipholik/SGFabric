#include <linux/if_ether.h>
#include <linux/ip.h>
#include <linux/icmp.h>
#include "ebpf_switch.h"

struct countentry
{
    int bytes;
    int packets;
};

struct bpf_map_def SEC("maps") assetdisc = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = 6, // MAC address is the key
    .value_size = sizeof(struct countentry),
    .max_entries = 256,
};

uint64_t prog(struct packet *pkt)
{
    struct countentry *item;

    if(pkt->eth.h_source == '000000000008') //TODO fix this! 
    {
        bpf_debug(1);

        if (bpf_map_lookup_elem(&assetdisc, pkt->eth.h_source, &item) == -1)
	{
	    struct countentry newitem = {
		    .bytes = 0,
		    .packets = 0,
	    };

            bpf_map_update_elem(&assetdisc, pkt->eth.h_source, &newitem, 0);
            item = &newitem;
        }  

    item->packets++;
    item->bytes += pkt->metadata.length;
       
    }    

    return NEXT;
}
char _license[] SEC("license") = "GPL";
