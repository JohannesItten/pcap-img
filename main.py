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
    f = open(f_bars_720p_2, "rb")
    pcap = dpkt.pcap.Reader(f)
    #given data
    video_width = 1280
    video_height = 720
    scan = _PROGRESSIVE
    depth = 10
    sampling = "YCrCb 4:2:2"
    directory = "test-images"
    #data, can be calculated
    pgroup_size = 5
    pgroup_coverage = 2
    pgroup_order = "CbY0CrY1" #provided: 0 1 2 3
    pixel_components_amount = 4 #amount of pixel components in pgroup
    pixel_needed_order = "YCrCb" #needed (1, 2, 0) (3, 2, 0)
    pgroup_shift = pgroup_size * 8 // pixel_components_amount

    image_buf = np.zeros((video_height, video_width, 3), dtype=np.uint16)
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
        #processing ST-2110-20 payload
        packet_number += 1
        st_payload = st.payload
        srd_field = st.srd_f
        srd_len = st.srd_len
        current_offsets = {}
        current_len = 0
        for i in range(0, len(st_payload), pgroup_size):
            if i + pgroup_size > len(st_payload):
                break
            if current_len > srd_len:
                break
            #processing pgroups
            srd_row = st.srd_row
            #Field Flag = 1 means second field/segment
            if (srd_field == 1):
                srd_row += video_height // 2
            srd_offset = st.srd_offset
            if srd_offset not in current_offsets:
                current_offsets[srd_offset] = srd_offset
            pgroup = int.from_bytes(st_payload[i:i+pgroup_size])
            pixel_comps = []
            for _ in range(pixel_components_amount):
                pixel_mask = (2 << (pgroup_shift - 1)) - 1
                pixel_comps.append(pgroup & pixel_mask)
                pgroup >>= pgroup_shift
            pixel_comps.reverse()
            #TODO: remove magic numbers
            #For YCrCb 10 bit, packet order: CbY0CrY1
            image_buf[srd_row, current_offsets[srd_offset]] = [
                pixel_comps[1],
                pixel_comps[2],
                pixel_comps[0]
            ]
            image_buf[srd_row, current_offsets[srd_offset] + 1] = [
                pixel_comps[3],
                pixel_comps[2],
                pixel_comps[0]
            ]
            current_offsets[srd_offset] += pgroup_coverage
            srd_len += pgroup_size * 8
        #end of frame or second field/segment
        if ((scan == _INTERLACED and rtp.m == 1 and srd_field == 1) or
            (scan == _PROGRESSIVE and rtp.m == 1)):
            print("Last packet received, saving image...")
            current_offsets = {}
            #TODO: figure out with OpenCV and sampling
            image_buf = (image_buf / 1023 * 255).astype(np.uint8)  # Convert to 8-bit for display
            converted_buf = cv2.cvtColor(image_buf, cv2.COLOR_YCrCb2BGR)
            cv2.imwrite(f"img-{packet_number}.png", converted_buf)
            image_buf = np.zeros((video_height, video_width, 3), dtype=np.uint16)

if __name__ == "__main__":
    main()