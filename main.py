import sys, argparse
import dpkt
import numpy as np
import cv2
import pgroup as pg
from srd import SampleRowData

_INTERLACED = 0
_PROGRESSIVE = 1
_MAX_ROW_VALUE = 32767 #max 15 bit value

def process_pcap(video_params):
    video = video_params
    pgroup = pg.Pgroup(colorspace=video.colorspace,
                       sampling=video.sampling,
                       depth=video.depth)
    image_buf = np.zeros((video.height, video.width, 3), dtype=np.uint16)
    packet_number = 0
    saved_images_amount = 0
    print("Reading PCAP file...")
    pcap = dpkt.pcap.Reader(video.filename)
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
            if (video.scan == _INTERLACED and segment.field == 1):
                current_row = current_row * 2 + 1
            elif (video.scan == _INTERLACED and segment.field == 0):
                current_row *= 2
            #packets with probably incompliant data
            bad_packets = []
            #process pgroups
            for i in range(0, segment.length, pgroup.size):
                if (i + pgroup.size > segment.length):
                    break
                pixels = pgroup.get_pixels(segment.data[i:i+pgroup.size])
                for p in pixels:
                    try:
                        image_buf[current_row, current_offset] = p
                    except IndexError:
                        if packet_number not in bad_packets:
                            print(f"Packet {packet_number} skipped...")
                            bad_packets.append(packet_number)
                    current_offset += 1
            #end of frame or second field/segment
            if ((video.scan == _INTERLACED and rtp.m == 1 and segment.field == 1) or
                (video.scan == _PROGRESSIVE and rtp.m == 1)):
                img_name = f"img-{packet_number}.png"
                print(f"Last packet received, saving image... {img_name}")
                save_image("test-images", img_name, video.colorspace, video.depth, image_buf)
                saved_images_amount += 1
            if (saved_images_amount <= 0):
                continue
            if (saved_images_amount >= video.limit):
                print(f"Reached image limit, which is: {video.limit}")
                return
    video.filename.close()


def save_image(path, name, colorspace, depth, img_buffer):
    #TODO: figure out with OpenCV and sampling
    if (depth > 8):
        # img_buffer = cv2.convertScaleAbs(img_buffer, alpha=(255.0/65535.0))
        img_buffer = (img_buffer / 1023 * 255).astype(np.uint8)  # Convert to 8-bit for display
    converted_buf = cv2.cvtColor(img_buffer, cv2.COLOR_YCrCb2BGR)
    cv2.imwrite(f"{path}/{name}", converted_buf)
    img_buffer = np.zeros(img_buffer.shape, dtype=np.uint8)

def is_resolution_valid(args):
    is_valid = True
    if ((args.width <= 0 or args.width > _MAX_ROW_VALUE) or 
    (args.height <= 0 or args.height > _MAX_ROW_VALUE)):
        is_valid = False
    return is_valid

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple tool to get images from ST-2110-20"
                                     " pcap files."
                                     " Please, notice, that all images will be converted"
                                     " to 8 bit RGB .png file.",
                                     epilog="https://github.com/JohannesItten/pcap-img")
    parser.add_argument("-f", "--filename",
                        help="pcap file absolute path",
                        required=True,
                        type=argparse.FileType(mode="rb"))
    parser.add_argument("-vw", "--width",
                        help="video width",
                        type=int,
                        required=True)
    parser.add_argument("-vh", "--height",
                        help="video height",
                        type=int,
                        required=True)
    parser.add_argument("-vs", "--scan", 
                        help="video scan",
                        choices=["i", "p"],
                        required=True)
    parser.add_argument("-c", "--colorspace",
                        help="colorspace",
                        choices=["YCbCr", "RGB"],
                        required=True)
    parser.add_argument("-s", "--sampling",
                        help="sampling",
                        choices=["4:2:2", "4:4:4"],
                        required=True)
    parser.add_argument("-d", "--depth",
                        help="bit depth",
                        type=int,
                        choices=[8, 10, 12, 16],
                        required=True)
    parser.add_argument("-l", "--limit",
                        help="image amount limit",
                        type=int,
                        default=-1,
                        required=False)
    #TODO: argparse error handling
    args = parser.parse_args()
    #TODO: add description to help message
    if  not is_resolution_valid(args):
        print(f"Incorrect video width or height. Possible values between 1 and {_MAX_ROW_VALUE}")
        sys.exit(-1)
    if (args.scan == "i"):
        args.scan = _INTERLACED
    elif (args.scan == "p"):
        args.scan = _PROGRESSIVE
    process_pcap(args)