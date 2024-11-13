/* GOOSE analyser for parsing GOOSE APDU data based on TLV format */

#include <linux/if_ether.h>
#include <linux/ip.h>
#include <linux/icmp.h>
#include "ebpf_switch.h"

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
    void *data = (void *)(unsigned long)&pkt->eth; 
    void *data_end = (void *)(unsigned long)&pkt->eth + pkt->metadata.length;

    if(pkt->eth.h_proto == 47240) //GOOSE = 0x88B8 (LittleE) -> B888 (BigE) = 47240 
    {
        if (bpf_map_lookup_elem(&goose_analyser, pkt->eth.h_source, &item) == -1)
	    {
            struct stsqnums newitem = {
                .stNum = -1,
                .sqNum = -1,
            };

            bpf_map_update_elem(&goose_analyser, pkt->eth.h_source, &newitem, 0);
            item = &newitem;
        }  
        struct ethhdr *eth = data; 
        unsigned char *ptr = (unsigned char *) (eth + 1); //This is start of the GOOSE Header
        ptr += 11; //Start of APDU (length of GOOSE Header 8 bytes + TL meta 3 bytes) 
        //bpf_notify(5, ptr, sizeof(ptr));

        while (ptr + 2 <= (unsigned char *)data_end){
            //bpf_notify(6, ptr, sizeof(ptr));
            __u8 tag = *ptr++; 
            __u8 length = *ptr++; 

            if (ptr + length > (unsigned char *)data_end) {
                return DROP; 
            }
            
            if(tag == 0x85) {  //stNum             
                if(length == 1) {
                    item->stNum = *((__u8 *)ptr); 
                }                
            }
            if(tag == 0x86) {  //sqNum             
                if(length == 1) {
                    item->sqNum = *((__u8 *)ptr); 
                }
                break; 
            }
            ptr += length; 
        }
    }    

    return NEXT;
}
char _license[] SEC("license") = "GPL";
