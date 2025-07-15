import sys, argparse, os
import dpkt
import numpy as np
import cv2
import st_2110_20.pgroup as pg
from st_2110_20.srd import SampleRowData

_INTERLACED = 0
_PROGRESSIVE = 1
_MAX_ROW_VALUE = 32767 #max 15 bit value

# TODO: move all printed texts to constants
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
        # TODO: less lazy RTP validity check https://www.freesoft.org/CIE/RFC/1889/51.htm
        # at least i should check rtp.v = 2 and rtp.pt in range [96-127]
        # https://pub.smpte.org/pub/st2110-10/st2110-10-2022.pdf
        # https://datatracker.ietf.org/doc/html/rfc4566#section-6
        if (rtp.version != 2 or rtp.pt < 96 or rtp.pt > 127):
            print(f"Packet {packet_number} skipped..."
                  "Probably not RTP")
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
                            print(f"Packet {packet_number} skipped..."
                                  " Probably incorrect video params given")
                            bad_packets.append(packet_number)
                    current_offset += 1
            #end of frame or second field/segment
            if ((video.scan == _INTERLACED and rtp.m == 1 and segment.field == 1) or
                (video.scan == _PROGRESSIVE and rtp.m == 1)):
                img_name = f"img-{packet_number}.png"
                print(f"Last packet received, saving image... {img_name}")
                save_image(video.directory, img_name, video.colorspace, video.depth, image_buf)
                image_buf = np.zeros(image_buf.shape, dtype=np.uint16)
                saved_images_amount += 1
            if (saved_images_amount <= 0):
                continue
            if (saved_images_amount >= video.limit):
                print(f"Reached image limit, which is: {video.limit}")
                return
    video.filename.close()


def save_image(directory, name, colorspace, depth, img_buffer):
    if (not os.path.isdir(directory) or
        not os.access(directory, os.W_OK)):
        print(f"Given directory {directory} for images does not exist or read-only")
    path = os.path.abspath(directory)
    conversion_type = cv2.COLOR_YCrCb2BGR
    if (colorspace == "RGB"):
        conversion_type = cv2.COLOR_RGB2BGR
    # Probably should fix it later, color bars must help
    # i am not sure about color accuracy, due to many conversions
    if depth < 16:
        color_multiplier = 1 << (16 - depth)
        img_buffer = (img_buffer * color_multiplier).astype(np.uint16)
    img_buffer = cv2.cvtColor(img_buffer, conversion_type)
    cv2.imwrite(f"{path}/{name}", img_buffer)

def create_args_parser():
    parser = argparse.ArgumentParser(description="Simple tool to get images from ST-2110-20"
                                     " pcap files."
                                     " Please, notice, that all images will be converted"
                                     " to 16 bit RGB .png file.",
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
    #optional ars
    parser.add_argument("-l", "--limit",
                        help="image amount limit",
                        type=int,
                        default=-1,
                        required=False)
    parser.add_argument("-dir", "--directory",
                        help="output directory for images",
                        default=".",
                        required=False)
    return parser

def is_resolution_valid(args):
    is_valid = True
    if ((args.width <= 0 or args.width > _MAX_ROW_VALUE) or 
    (args.height <= 0 or args.height > _MAX_ROW_VALUE)):
        is_valid = False
    return is_valid

if __name__ == "__main__":
    parser = create_args_parser()
    #TODO: argparse error handling
    args = parser.parse_args()
    if  not is_resolution_valid(args):
        print(f"Incorrect video width or height. Possible values between 1 and {_MAX_ROW_VALUE}")
        sys.exit(-1)
    if (args.scan == "i"):
        args.scan = _INTERLACED
    elif (args.scan == "p"):
        args.scan = _PROGRESSIVE
    process_pcap(args)