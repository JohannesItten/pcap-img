import dpkt
import numpy as np
import cv2
import pgroup as pg
from srd import SampleRowData, SampleRowDataSegment, SampleRowDataHeader

_INTERLACED = 0
_PROGRESSIVE = 1

def main():
    print("Reading PCAP file...")
    f_bars_720p_1 = "pcap/ST2110-20_720p_59_94_color_bars.pcap"
    f_bars_720p_2 = "pcap/ST2110-20_720p_59_94_color_bars_vendor_2.pcap"
    f_bars_1080i_1 = "pcap/ST2110-20_1080i_59_94_color_bars.pcap"
    own_pcap_1 = "own-pcap/1.pcap"
    f = open(f_bars_720p_1, "rb")
    pcap = dpkt.pcap.Reader(f)
    #given data
    video_width = 1280
    video_height = 720
    scan = _PROGRESSIVE
    colorspace = "YCbCr"
    sampling = "4:2:2"
    depth = 10
    directory = "test-images"
    image_limit = 10
    saved_images_amount = 0
    #end of user data
    pgroup = pg.Pgroup(colorspace=colorspace,
                       sampling=sampling,
                       depth=depth)
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
        srd = SampleRowData(rtp.data)
        for segment in srd.segments:
            current_row = segment.row
            current_offset = segment.offset
            if (scan == _INTERLACED and segment.field == 1):
                current_row = current_row * 2 + 1
            elif (scan == _INTERLACED and segment.field == 0):
                current_row *= 2
            #process pgroups
            for i in range(0, segment.length, pgroup.size):
                pixels = pgroup.get_pixels(segment.data[i:i+pgroup.size])
                for p in pixels:
                    image_buf[current_row, current_offset] = p
                    current_offset += 1
            #end of frame or second field/segment
            if ((scan == _INTERLACED and rtp.m == 1 and segment.field == 1) or
                (scan == _PROGRESSIVE and rtp.m == 1)):
                print("Last packet received, saving image...")
                #TODO: figure out with OpenCV and sampling
                image_buf = (image_buf / 1023 * 255).astype(np.uint8)  # Convert to 8-bit for display
                converted_buf = cv2.cvtColor(image_buf, cv2.COLOR_YCrCb2BGR)
                cv2.imwrite(f"{directory}/img-{packet_number}.png", converted_buf)
                image_buf = np.zeros((video_height, video_width, 3), dtype=np.uint16)
                saved_images_amount += 1
            if (saved_images_amount >= image_limit):
                print(f"Reached image limit, which is: {image_limit}")
                break

if __name__ == "__main__":
    main()