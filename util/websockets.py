import hashlib
import base64


class Frame:
    def __init__(self):
        self.fin_bit = 0  # An int with the value of the fin bit (Either 1 or 0)
        self.opcode = 0  # e.g. if the op code is bx1000, this field stores 8 as an int
        self.payload_length = 0  # The payload length as an int. Your function must handle all 3 payload length modes
        self.payload = b""  # The unmasked bytes of the payload
        self.mask_bit = 0


def compute_accept(websocket: str) -> str:
    GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    combined = websocket + GUID
    # output in binary, because base64 only takes that in
    hashed_combined = hashlib.sha1(combined.encode('utf-8')).digest()
    return base64.b64encode(hashed_combined).decode('utf-8')


def opcode_helper(binary: str) -> int:
    expo = 3
    out = 0
    for char in binary:
        out += (2 ** expo) * int(char)
        expo -= 1
    return out


def parse_ws_frame(frame_bytes: bytes) -> Frame:
    out = Frame()
    # frame_bits = ''.join(f'{byte:08b}' for byte in frame_bytes)
    mask = (frame_bytes[1] >> 7) & 0x01
    out.mask_bit = mask
    out.fin_bit = (frame_bytes[0] >> 7) & 0x01
    out.opcode = frame_bytes[0] & 0x0F
    if (frame_bytes[1] & 0x7F) < 126:
        out.payload_length = frame_bytes[1] & 0x7F
        mask_key_start = 2
    elif (frame_bytes[1] & 0x7F) == 126:
        # out.payload_length = frame_bytes[2:4] & 0xFFFF
        out.payload_length = int.from_bytes(frame_bytes[2:4], byteorder='big')
        mask_key_start = 4
    else:
        # out.payload_length = frame_bytes[2:10] & 0xFFFFFFFFFFFFFFFF
        out.payload_length = int.from_bytes(frame_bytes[2:10], byteorder='big')
        mask_key_start = 10

    if mask == 0:
        out.payload = frame_bytes[mask_key_start:]
    else:
        masking_key = frame_bytes[mask_key_start:mask_key_start + 4]
        unmasked_payload = bytearray(out.payload_length)
        for i in range(0, out.payload_length, 4):
            for j in range(4):
                if i + j < out.payload_length:
                    unmasked_payload[i + j] = frame_bytes[mask_key_start + 4 + i + j] ^ masking_key[j]
        out.payload = unmasked_payload
    return out


def generate_ws_frame(data: bytes) -> bytes:
    find_op = 0x81
    data_length = len(data)
    if data_length <= 125:
        # Use 1 byte to represent payload length
        mask_len = data_length
        header = bytes([find_op, mask_len])
    elif data_length < 65536:
        # Use 2 bytes for extended payload length
        mask_len = 126
        header = bytes([find_op, mask_len]) + data_length.to_bytes(2, byteorder='big')
    else:
        # Use 8 bytes for extended payload length
        mask_len = 127
        header = bytes([find_op, mask_len]) + data_length.to_bytes(8, byteorder='big')

    # Combine header and data to form the complete WebSocket frame
    frame = header + data
    return frame


if __name__ == '__main__':
    # bytes = b"1"
    #
    # stuff = ''.join(f'{byte:08b}' for byte in bytes)
    # print(stuff)
    int_val = 1
    # find_op = 0x81
    # mask_len = 0x00
    # header = find_op + mask_len
    # print(header)
    # print(value.to_bytes(1, 'big'))
    stuff = "7zYWyzJ7vj4HBVZgSzt6zQ=="
    print(compute_accept(stuff))
