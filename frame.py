# -*- coding: utf-8 -*-
"""
-------------------------------------------------
# @Project  :GBN_Pro
# @File     :Frame
# @Date     :2021/6/3 13:20
# @Author   :CuiChenxi
# @Email    :billcuichenxi@163.com
# @Software :PyCharm
-------------------------------------------------
"""
from configuration import MAX_SEQ
class Frame:
    def __init__(self,frame_nr,frame_expected,port):
        self.sender=port
        self.data=''
        self.seq=frame_nr
        self.ack= (frame_expected+MAX_SEQ)%(MAX_SEQ+1)
        self.checksum=''
        #print("frame_expected={}".format(frame_expected))
