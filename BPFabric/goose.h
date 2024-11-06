/*
 * GOOSE	An implementation of the GOOSE protocol suite for the LINUX
 *		operating system.  
 *
 *		Global definitions for the IEC 61850 GOOSE protocol.
 *
 * Version:	@(#)goose.h	0.0.1a	06/11/2024
 *
 * Author:	Filip Holik, <filip.holik@glasgow.ac.uk>
 *
 *		This program is free software; you can redistribute it and/or
 *		modify it under the terms of the GNU General Public License
 *		as published by the Free Software Foundation; either version
 *		2 of the License, or (at your option) any later version.
 */

//#ifndef _LINUX_IF_ETHER_H
//#define _LINUX_IF_ETHER_H

#include <linux/if_ether.h>
#include <linux/types.h>

/*
 *	IEEE 802.3 Ethernet magic constants.  The frame sizes omit the preamble
 *	and FCS/CRC (frame check sequence).
 */

#define APPID	2		/* Octets in one ethernet addr	 */
#define LEN	2		/* Total octets in header.	 */
#define RESERVED	4		/* Min. octets in frame sans FCS */
#define GO_CB_REF	2		/* Max. octets in payload	 */
#define TTL	2		/* Max. octets in frame sans FCS */
#define DAT_SET	2		/* Octets in the FCS		 */
#define GID	2		/* Octets in the FCS		 */
#define T	8		/* Octets in the FCS		 */
#define ST_NUM	1		/* Octets in the FCS		 */
#define SQ_NUM	1		/* Octets in the FCS		 */


struct goose_hdr {
	//unsigned char	h_dest[ETH_ALEN];	/* destination eth addr	*/
	//unsigned char	h_source[ETH_ALEN];	/* source ether addr	*/
	//__be16		h_proto;		/* packet type ID field	*/    
    __u16 app_id; 
    __u16 length;
    __u16 reserved1;
    __u16 reserved2; 
} __attribute__((packed));


struct goose_apdu {
    __u16 go_cb_ref; 
    __u16 ttl;
    __u16 dat_set;
    __u16 gid; 
    __u64 t; 
    __u8 st_num; 
    __u8 sq_num; 
} __attribute__((packed));



