import dpkt
import socket
import cv2
import numpy as np

#simple remainder of rtp st2110-20 packet structure
#eth header
#ip header
#udp header
#rtp header
#payload header
#pgroups
#eth footer

def main():
    print("Reading PCAP file...")
    f = open("pcap/ST2110-20_720p_59_94_color_bars.pcap", "rb")
    pcap = dpkt.pcap.Reader(f)
    amount = 0
    for _, buf in pcap:
        eth = dpkt.ethernet.Ethernet(buf)
        if not isinstance(eth.data, dpkt.ip.IP):
            continue
        ip = eth.data
        if not isinstance(ip.data, dpkt.udp.UDP):
            continue
        udp = ip.data
        #TODO: check if udp.data is rtp
        amount += 1
        rtp = dpkt.rtp.RTP(udp.data)
        #processing only frame last packets to reduce output test data
        if rtp.m == 1:
            print("RTP packet with M bit set:", amount, rtp.pt)
            #smpte 2110-20 payload header (first 8 bytes of rtp payload)
            #TODO: read about length of ST 2110-20 payload header
            #and true meaning of C bit
            smpte_payload_header = rtp.data[:8]
            #srd_len = pgroup amount x pgroup size in bytes
            srd_len = int.from_bytes(smpte_payload_header[2:4], byteorder='big')
            print("srd len:", srd_len)
            srd_row_bytes = int.from_bytes(smpte_payload_header[4:6])
            print("field identification flag:", srd_row_bytes & 1)
            all_except_first_mask = (1 << srd_row_bytes.bit_length()) - 1
            print("srd row number:", srd_row_bytes & all_except_first_mask)
            srd_offset_bytes = int.from_bytes(smpte_payload_header[6:8])
            print("continuation flag:", srd_offset_bytes & 1)
            print("srd offset:", srd_offset_bytes & all_except_first_mask)
            smpte_payload_data = rtp.data[8:]
            # try to decode sample as YCbCr 4:2:2 10 bits
            # 2 pixel in 40 bits (5 octets)
            for i in range(0, len(smpte_payload_data), 5):
                if i + 5 > len(smpte_payload_data):
                    break
                print(smpte_payload_data[i:i+5].hex())

    print("packets amount: ", amount)

def inet_to_str(inet):
    """Convert inet object to a string

        Args:
            inet (inet struct): inet network address
        Returns:
            str: Printable/readable IP address
    """
    # First try ipv4 and then ipv6
    try:
        return socket.inet_ntop(socket.AF_INET, inet)
    except ValueError:
        return socket.inet_ntop(socket.AF_INET6, inet)

if __name__ == "__main__":
    main()