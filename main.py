import dpkt
import st2110_20
import numpy as np
import cv2

_INTERLACED = 0
_PROGRESSIVE = 1

def main():
    print("Reading PCAP file...")
    f_bars_720p_1 = "pcap/ST2110-20_720p_59_94_color_bars.pcap"
    f_bars_720p_2 = "pcap/ST2110-20_720p_59_94_color_bars_vendor_2.pcap"
    f_bars_1080i_1 = "pcap/ST2110-20_1080i_59_94_color_bars.pcap"
    f = open(f_bars_1080i_1, "rb")
    pcap = dpkt.pcap.Reader(f)
    #given data
    video_width = 1920
    video_height = 1080
    scan = _INTERLACED
    depth = 10
    sampling = "YCrCb 4:2:2"
    directory = "test-images"
    #data, can be calculated
    pgroup_size = 5
    pgroup_coverage = 2
    pixel_components_amount = 4 #amount of pixel components in pgroup
    pgroup_shift = pgroup_size * 8 // pixel_components_amount
    pixel_mask = (2 << (pgroup_shift - 1)) - 1
    pixel_shift_multipliers = [[2, 1, 3], [0, 1, 3]]

    image_buf = np.zeros((video_height, video_width, 3), dtype=np.uint16)
    packet_number = 0
    for _, buf in pcap:
        packet_number += 1
        eth = dpkt.ethernet.Ethernet(buf)
        if not isinstance(eth.data, dpkt.ip.IP):
            continue
        ip = eth.data
        if not isinstance(ip.data, dpkt.udp.UDP):
            continue
        udp = ip.data
        rtp = dpkt.rtp.RTP(udp.data)
        st = st2110_20.ST2110_20(rtp.data)
        #processing ST-2110-20 header
        srd_field = st.srd_f
        # srd_len = st.srd_len
        srd_row = st.srd_row
        srd_offset = st.srd_offset
        #processing pgroups
        st_payload = st.payload
        current_offsets = {}
        #Field Flag = 1 means second field/segment
        if (scan == _INTERLACED and srd_field == 1):
            srd_row = srd_row * 2 + 1
        elif (scan == _INTERLACED and srd_field == 0):
            srd_row *= 2
        for i in range(0, len(st_payload), pgroup_size):
            if i + pgroup_size > len(st_payload):
                break
            if srd_offset not in current_offsets:
                current_offsets[srd_offset] = srd_offset
            pgroup = int.from_bytes(st_payload[i:i+pgroup_size])
            #Pixel components
            for multipliers in pixel_shift_multipliers:
                pixel_comps = []
                for m in multipliers:
                    comp = (pgroup >> (m * pgroup_shift)) & pixel_mask
                    pixel_comps.append(comp)
                image_buf[srd_row, current_offsets[srd_offset]] = pixel_comps
                current_offsets[srd_offset] += 1
        #end of frame or second field/segment
        if ((scan == _INTERLACED and rtp.m == 1 and srd_field == 1) or
            (scan == _PROGRESSIVE and rtp.m == 1)):
            print("Last packet received, saving image...")
            current_offsets = {}
            #TODO: figure out with OpenCV and sampling
            image_buf = (image_buf / 1023 * 255).astype(np.uint8)  # Convert to 8-bit for display
            converted_buf = cv2.cvtColor(image_buf, cv2.COLOR_YCrCb2BGR)
            cv2.imwrite(f"test-images/img-{packet_number}.png", converted_buf)
            image_buf = np.zeros((video_height, video_width, 3), dtype=np.uint16)

if __name__ == "__main__":
    main()