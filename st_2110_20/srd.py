"""
RFC 4175 datagram (https://datatracker.ietf.org/doc/html/rfc4175):

0                   1                   2                   3
0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| V |P|X|   CC  |M|    PT       |       Sequence Number         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                           Time Stamp                          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                             SSRC                              |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|   Extended Sequence Number    |            Length             |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|F|          Line No            |C|           Offset            |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|            Length             |F|          Line No            |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|C|           Offset            |                               .
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+                               .
.                                                               .
.                 Two (partial) lines of video data             .
.                                                               .
+---------------------------------------------------------------+

RTP packet shall not contain more, than 3 SRD Headers
1 SRD Header = 6 bytes
"""

_MAX_SRD_AMOUNT = 3
_SRD_HEADER_SIZE = 6
_ESN_SIZE = 2
_HEADER_FLAG_SHIFT = 15

class SampleRowDataHeader:
    def __init__(self, data: bytes):
        self.length = int.from_bytes(data[:2], byteorder="big")
        row = int.from_bytes(data[2:4], byteorder="big")
        offset = int.from_bytes(data[4:6], byteorder="big")
        offset_row_mask = (1 << _HEADER_FLAG_SHIFT) - 1
        self.field = row >> _HEADER_FLAG_SHIFT
        self.continuos = offset >> _HEADER_FLAG_SHIFT
        self.row = row & offset_row_mask
        self.offset = offset & offset_row_mask


class SampleRowDataSegment:
    def __init__(self, header: SampleRowDataHeader, data: bytes):
        self.length = header.length
        self.field = header.field
        self.row = header.row
        self.offset = header.offset
        self.data = data


class SampleRowData:
    def __init__(self, data: bytes):
        self.esn = int.from_bytes(data[:_ESN_SIZE], byteorder="big")
        self.headers = self._get_headers(data[_ESN_SIZE:_MAX_SRD_AMOUNT * _SRD_HEADER_SIZE])
        header_len = _ESN_SIZE + (len(self.headers) * _SRD_HEADER_SIZE)
        segments_data = data[header_len:]
        self.segments = self._get_segments(segments_data=segments_data)


    def _get_headers(self, headers_data: bytes):
        headers = []
        for i in range(0, len(headers_data), _SRD_HEADER_SIZE):
            head = SampleRowDataHeader(data=headers_data)
            headers.append(head)
            if head.continuos == 0:
                break
        return headers
    
    #returns each SRD segment with its corresponded header
    def _get_segments(self, segments_data: bytes):
        segments = []
        prev_srd_len = 0
        for header in self.headers:
            # TODO: should ask about that someone
            # cause ST-2110-20 leaves me with some questions
            srd_len = header.length
            if srd_len == 0:
                break
            seg = SampleRowDataSegment(header, segments_data[prev_srd_len:srd_len])
            segments.append(seg)
        return segments

            