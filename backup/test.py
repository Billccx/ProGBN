def crc16(buffer):
    c, treat, bcrc, wcrc = 0, 0, 0, 0
    for i in range(len(buffer)):
        #c=int(buffer[i])
        c = ord(buffer[i])
        for j in range(8):
            treat = c & 0x80
            c <<= 1
            bcrc = (wcrc >> 8) & 0x80
            wcrc <<= 1
            wcrc %= (0xffff + 1)
            if treat != bcrc:
                wcrc ^= 0x1021
    return wcrc


buffer = '\x30\x30\x30\x31\x30\x31'
crc = crc16(buffer)
print(hex(crc))

buffer2 = '\x30\x30\x30\x31\x30\x39\x30\x46\x46'
crc = crc16(buffer2)
print(hex(crc))


buffer3 = '\x30\x31\x30\x30\x31\x30\x30\x31'
crc = crc16(buffer3)
print(hex(crc))


crch = crc >> 8
crcl = crc & 0x00ff

print(hex(crch), hex(crcl))

lll = [1, 2, 3]
print(lll[1:3])
