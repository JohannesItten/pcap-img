import dpkt
import cv2
import numpy as np

def main():
    print("Reading PCAP file...")
    f = open("pcap/ST2110-20_1080i_59_94_color_bars.pcap", "rb")
    pcap = dpkt.pcap.Reader(f)
    amount = 0
    image_data = np.zeros((1080, 1920, 3), dtype=np.uint16)
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
        # if (rtp.ts not in [2460244688, 2460246189]):
        #     continue
        #smpte 2110-20 payload header (first 8 bytes of rtp payload)
        #TODO: read about length of ST 2110-20 payload header
        #and true meaning of C bit
        smpte_payload_header = rtp.data[:8]
        #srd_len = pgroup amount x pgroup size in bytes
        srd_row_bytes = int.from_bytes(smpte_payload_header[4:6])
        srd_field_flag = (srd_row_bytes >> 15) & 1
        all_except_first_mask = (1 << 15) - 1
        srd_row = srd_row_bytes & all_except_first_mask
        srd_offset_bytes = int.from_bytes(smpte_payload_header[6:8])
        all_except_first_mask = (1 << srd_offset_bytes.bit_length()) - 1
        srd_offset = srd_offset_bytes & all_except_first_mask
        smpte_payload_data = rtp.data[8:]
        # try to decode sample as YCbCr 4:2:2 10 bits
        # 2 pixel in 40 bits (5 octets)
        current_srd_offset = {}
        if srd_field_flag == 1:
            srd_row += 540  # Adjust for field identification flag
        for i in range(0, len(smpte_payload_data), 5):
            if i + 5 > len(smpte_payload_data):
                break
            #bad solution, but ok for opencv & numpy test
            if srd_offset not in current_srd_offset:
                current_srd_offset[srd_offset] = srd_offset
            #color data in reverse order
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
        if rtp.m == 1 and srd_field_flag:
            print("Last packet received, saving image...")
            image_data = (image_data / 1023 * 255).astype(np.uint8)  # Convert to 8-bit for display
            converted_image = cv2.cvtColor(image_data, cv2.COLOR_YCrCb2BGR)
            cv2.imwrite("test" + str(amount) + ".png", converted_image)
            image_data = np.zeros((1080, 1920, 3), dtype=np.uint16)
    print("packets amount: ", amount)

if __name__ == "__main__":
    # main()
    main()