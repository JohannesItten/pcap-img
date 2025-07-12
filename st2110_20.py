from dpkt import Packet

class ST2110_20(Packet):
    """SMPTE ST 2110-20 Packet.

    Attributes:
        __hdr__: Header fields of ST 2110-20.
    """
    
    _ESN_MASK = 0x8000
    _SRD_LEN_MASK = 0x7FFF
    _FIELD_ID_MASK = 0x8000
    _SRD_ROW_MASK = 0x7FFF
    _SRD_CONTINUATION_MASK = 0x01
    _SRD_OFFSET_MASK = 0x7FFF
    _ESN_SHIFT = 15

    __hdr__ = (
        #Sample Row Data (SRD) header fields
        #esn - Extended Sequence Number (16 bits)
        #srd_len - Sample Row Data Length (16 bits)
        #srd_f - Field Identification Flag (1 bit)
        #srd_row - Sample Row Data Number (15 bits)
        #srd_c - Continuation Flag (1 bit)
        #srd_offset - Sample Row Data Offset (15 bits)
    )


    @property
    def esn(self):
        return int.from_bytes(self.data[:2])
    
    @property
    def srd_len(self):
        return int.from_bytes(self.data[2:4])
    
    @property
    def srd_f(self):
        return int.from_bytes(self.data[4:6]) >> 15 & 1
    
    @property
    def srd_row(self):
        return int.from_bytes(self.data[4:6]) & ((1 << 15) - 1)
    
    @property
    def srd_c(self):
        return int.from_bytes(self.data[6:8]) >> 15 & 1
    
    @property
    def srd_offset(self):
        return int.from_bytes(self.data[6:8]) & ((1 << 15) - 1)
    
    @property
    def payload(self):
        return self.data[8:]