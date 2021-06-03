# -*- coding: utf-8 -*-
"""
-------------------------------------------------
# @Project  :GBN_Pro
# @File     :crc
# @Date     :2021/6/3 14:35
# @Author   :CuiChenxi
# @Email    :billcuichenxi@163.com
# @Software :PyCharm
-------------------------------------------------
"""


def Crc16(x, invert):
    a = 0xFFFF
    b = 0xA001
    for byte in x:
        a ^= ord(byte)
        for i in range(8):
            last = a % 2
            a >>= 1
            if last == 1:
                a ^= b
    s = hex(a).upper()

    return s[4:6] + s[2:4] if invert == True else s[2:4] + s[4:6]


def crc16(buffer):
    c, treat, bcrc, wcrc = 0, 0, 0, 0
    for i in range(len(buffer)):
        c = int(buffer[i])
        for j in range(8):
            treat = c & 0x80
            c <<= 1
            bcrc = (wcrc >> 8) & 0x80
            wcrc <<= 1
            wcrc %= (0xffff + 1)
            if treat != bcrc:
                wcrc ^= 0x1021
    return wcrc




