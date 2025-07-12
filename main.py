import dpkt
import st2110_20

def main():
    print("Reading PCAP file...")
    f = open("pcap/ST2110-20_720p_59_94_color_bars.pcap", "rb")
    pcap = dpkt.pcap.Reader(f)
    packet_number = 0
    for _, buf in pcap:
        eth = dpkt.ethernet.Ethernet(buf)
        if not isinstance(eth.data, dpkt.ip.IP):
            continue
        ip = eth.data
        if not isinstance(ip.data, dpkt.udp.UDP):
            continue
        udp = ip.data
        rtp = dpkt.rtp.RTP(udp.data)
        st = st2110_20.ST2110_20(rtp.data)
        packet_number += 1
        if packet_number > 20:
            break
        print(f"Packet {packet_number}:")
        print(f"ESN: {st.esn}")
        print(f"SRD Len: {st.srd_len}")
        print(f"Field ID Flag: {st.srd_f}")
        print(f"SRD Row: {st.srd_row}")
        print(f"SRD C Flag: {st.srd_c}")
        print(f"SRD Offset: {st.srd_offset}")
        print()
        st_payload = st.payload

if __name__ == "__main__":
    main()