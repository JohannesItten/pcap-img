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
            print("field identification flag:", srd_row_bytes & (1 << 15))
            all_except_first_mask = (1 << srd_row_bytes.bit_length()) - 1
            print("srd row number:", srd_row_bytes & all_except_first_mask)
            srd_offset_bytes = int.from_bytes(smpte_payload_header[6:8])
            print("continuation flag:", srd_offset_bytes & 1)
            print("srd offset:", srd_offset_bytes & all_except_first_mask)
            smpte_payload_data = rtp.data[8:]
            # try to decode sample as YCbCr 4:2:2 10 bits
            # 2 pixel in 40 bits (5 octets)
            pixel_amount = (len(smpte_payload_data) // 5) // 2
            print("Pixels in this packet:", pixel_amount)
            for i in range(0, len(smpte_payload_data), 5):
                if i + 5 > len(smpte_payload_data):
                    break
                #print(smpte_payload_data[i:i+5].hex())
            print()

    print("packets amount: ", amount)

def test_cv():
    print("Reading PCAP file...")
    f = open("pcap/ST2110-20_720p_59_94_color_bars.pcap", "rb")
    pcap = dpkt.pcap.Reader(f)
    amount = 0
    image_data = np.zeros((720, 1280, 3), dtype=np.uint16)
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
        #smpte 2110-20 payload header (first 8 bytes of rtp payload)
        #TODO: read about length of ST 2110-20 payload header
        #and true meaning of C bit
        smpte_payload_header = rtp.data[:8]
        #srd_len = pgroup amount x pgroup size in bytes
        srd_row_bytes = int.from_bytes(smpte_payload_header[4:6])
        all_except_first_mask = (1 << srd_row_bytes.bit_length()) - 1
        srd_row = srd_row_bytes & all_except_first_mask
        srd_offset_bytes = int.from_bytes(smpte_payload_header[6:8])
        all_except_first_mask = (1 << srd_offset_bytes.bit_length()) - 1
        srd_offset = srd_offset_bytes & all_except_first_mask
        smpte_payload_data = rtp.data[8:]
        # try to decode sample as YCbCr 4:2:2 10 bits
        # 2 pixel in 40 bits (5 octets)
        current_srd_offset = {}
        for i in range(0, len(smpte_payload_data), 5):
            if i + 5 > len(smpte_payload_data):
                break
            #bad solution, but ok for opencv & numpy test
            bits_str = ""
            for j in range(5):
                bits_str += bin(smpte_payload_data[i + j])[2:].zfill(8)
            if srd_offset not in current_srd_offset:
                current_srd_offset[srd_offset] = srd_offset
            color_data = []
            pgroup = int.from_bytes(smpte_payload_data[i:i+5], byteorder='big')
            for _ in range(4):
                color_data.append(pgroup & 1023)
                pgroup >>= 10
            color_data.reverse()
            y = color_data[1]
            cb = color_data[0]
            cr = color_data[2]
            y2 = color_data[3]
            image_data[srd_row, current_srd_offset[srd_offset]] = [y, cr, cb]
            image_data[srd_row, current_srd_offset[srd_offset] + 1] = [y2, cr, cb]
            current_srd_offset[srd_offset] += 2
            #end of bad solution
            #image_data[srd_row, srd_offset] = [0, 0, 0]
            # ((1 << X) - 1) << startBit get X bits starting from startBit
        if rtp.m == 1:
            print("Last packet recieved. Saving image...")
            image_data = (image_data / 1023 * 255).astype(np.uint8)  # Convert to 8-bit for display
            converted_image = cv2.cvtColor(image_data, cv2.COLOR_YCrCb2BGR)
            cv2.imwrite("test_" + str(amount) + ".png", converted_image)
            image_data = np.zeros((720, 1280, 3), dtype=np.uint16)
    print("packets amount: ", amount)

if __name__ == "__main__":
    # main()
    test_cv()