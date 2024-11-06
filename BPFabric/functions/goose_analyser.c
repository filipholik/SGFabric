#include <linux/if_ether.h>
#include <linux/ip.h>
#include <linux/icmp.h>
#include "ebpf_switch.h"
#include "goose.h"

struct stsqnums
{
    int stNum;
    int sqNum;
};

struct bpf_map_def SEC("maps") goose_analyser = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = 6, // MAC address is the key
    .value_size = sizeof(struct stsqnums),
    .max_entries = 256,
};

uint64_t prog(struct packet *pkt)
{
    struct stsqnums *item;
    //void *data = (void *)(unsigned long)&pkt->eth; 
    //struct ethhdr *eth = data; 

    if(pkt->eth.h_proto == 47240) //GOOSE = 0x88B8 (LittleE) -> B888 (BigE) = 47240 
    {
        //bpf_debug(1);
        struct goose_hdr *ghdr = (struct goose_hdr *) (&pkt->eth + 1); 
        struct goose_apdu *apdu = (struct goose_apdu *)(ghdr + 1); 

        if (bpf_map_lookup_elem(&goose_analyser, pkt->eth.h_source, &item) == -1)
	    {
            struct stsqnums newitem = {
                .stNum = -1,
                .sqNum = -1,
            };

            bpf_map_update_elem(&goose_analyser, pkt->eth.h_source, &newitem, 0);
            item = &newitem;
        }  

    item->stNum = apdu->st_num; 
    item->sqNum = apdu->sq_num; 
       
    //bpf_notify(0, apdu->st_num, sizeof(apdu->st_num));
    }    

    return NEXT;
}
char _license[] SEC("license") = "GPL";
