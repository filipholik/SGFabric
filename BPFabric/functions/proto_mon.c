/* Function for communication protocol monitoring, testing version */

#include <linux/if_ether.h>
#include <linux/ip.h>
#include <netinet/tcp.h>
#include <linux/icmp.h>
#include "ebpf_switch.h"

struct countentry
{
    int bytes_eth;
    int bytes_arp; 
    int bytes_ip4;
    int bytes_ip6;
    int bytes_tcp;
    int bytes_udp;
};

struct bpf_map_def SEC("maps") monitor = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = 6, // MAC address is the key
    .value_size = sizeof(struct countentry),
    .max_entries = 256,
};

uint64_t prog(struct packet *pkt)
{
    struct countentry *item;    

    if (bpf_map_lookup_elem(&monitor, pkt->eth.h_source, &item) == -1)
    {
        struct countentry newitem = {
            .bytes_eth = 0,
            .bytes_arp = 0,
            .bytes_ip4 = 0,
            .bytes_ip6 = 0,
            .bytes_tcp = 0,
            .bytes_udp = 0,
        };

        bpf_map_update_elem(&monitor, pkt->eth.h_source, &newitem, 0);
        item = &newitem;
    }

    //Ethernet 
    item->bytes_eth += pkt->metadata.length;

    if (pkt->eth.h_proto == 8){ //IPv4, 0x0008
        item->bytes_ip4 += pkt->metadata.length;

        struct ip *ipv4 = (struct ip *)(((uint8_t *)&pkt->eth) + ETH_HLEN);

        /*if (ipv4->ip_p == 6) { //TCP
            item->bytes_tcp += pkt->metadata.length;
        }
        if (ipv4->ip_p == 17) { //UDP
            item->bytes_udp += pkt->metadata.length;
        }*/          
    }  
    if (pkt->eth.h_proto == 1544){ //ARP, 0x0608
        item->bytes_arp += pkt->metadata.length;
    }  
    if (pkt->eth.h_proto == 56710){ //IPv6, 0xDD86
        item->bytes_ip6 += pkt->metadata.length;
    } 
       
    //bpf_notify(0, pkt->eth.h_source, sizeof(pkt->eth.h_source));
   
    return NEXT;
}
char _license[] SEC("license") = "GPL";
