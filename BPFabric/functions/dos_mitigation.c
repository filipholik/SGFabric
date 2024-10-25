#include <linux/if_ether.h>
#include <linux/ip.h>
#include <linux/icmp.h>
#include "ebpf_switch.h"


uint64_t prog(struct packet *pkt)
{
    //GOOSE = 0x88B8 (LittleE) -> B888 (BigE) = 47240 
    //SV = 0x88BA (LittleE) -> BA88 (BigE) = 47752
    //ARP = 0x0806 (LittleE) -> 0608 (BigE) = 1544
    if(pkt->eth.h_proto == 47240 || pkt->eth.h_proto == 47752 || pkt->eth.h_proto == 1544) 
    {      
        //bpf_debug(1);
        return NEXT;
        //bpf_notify(0, pkt->eth.h_source, sizeof(pkt->eth.h_source));
    }else   
    {
        //bpf_debug(2);
        return DROP;
    }    
}
char _license[] SEC("license") = "GPL";
