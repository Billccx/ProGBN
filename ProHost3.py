# -*- coding: utf-8 -*-
"""
-------------------------------------------------
# @Project  :GBN_Pro
# @File     :ProHost3
# @Date     :2021/6/3 16:12
# @Author   :CuiChenxi
# @Email    :billcuichenxi@163.com
# @Software :PyCharm
-------------------------------------------------
"""
import socket
import threading
import queue
import argparse
import pickle
import time
import sys
from frame import *
from configuration import *
from crc import *

MAX_SEQ = 7
port = 41321
Timeout = 1000
basetime = time.time() * 1000

QueueSet = {}
threadPool = []


def CreatPacket(frame_nr, frame_expected, p, buffer, snedFinished):
    # ack=frame_expected-1
    s = Frame(frame_nr, frame_expected, port)
    if not snedFinished:
        s.data = buffer[p]
        if (not RandomDecide(ErrorRate)):
            s.checksum = crc16(s.data)
        else:
            print("send CRC error")
    return s


def Receive(localsocket, filepath,targetaddr):
    cnt = 0

    # 开启定点发送线程
    QueueSet[targetaddr[1]] = queue.Queue()
    threadPool.append(threading.Thread(
        target=Solve,
        args=[localsocket, filepath, targetaddr[1]]
    ))
    threadPool[cnt].start()
    cnt += 1

    while (True):
        try:
            data, __address = localsocket.recvfrom(1024)
            r = pickle.loads(data)
            tempport = r.sender
            if (tempport in QueueSet):
                QueueSet[tempport].put(r)
            else:
                print("port {} 已接入".format(tempport))
                QueueSet[tempport] = queue.Queue()
                QueueSet[tempport].put(r)
                threadPool.append(threading.Thread(
                    target=Solve,
                    args=[localsocket, filepath, tempport]
                ))
                threadPool[cnt].start()
                cnt += 1
        except:
            # print("接收出错")
            pass


def between(a, b, c):
    if ((a <= b) and (b < c) or (c < a) and (a <= b) or (b < c) and (c < a)):
        return True
    else:
        return False


def Solve(clientsocket, filepath, tempport):
    sendId = 0
    recvId=0
    isEmpty = 0
    sendFinisfed = False
    setTime = False
    postTime = 0

    emptyTimer=0
    isemptyTimerSet=False

    otherhostset = False
    otherhost = 0  # 对方的host

    # 读取要发送的文件至缓冲区中
    buffer = []
    buffersz = 0
    bufferp = 0  # 缓冲区指针
    f = open(filepath, 'rb')
    while True:
        seq = f.read(600)
        if len(seq) > 0:
            buffer.append(seq)
            buffersz += 1
        else:
            break

    # 接收区
    receiver = b''

    next_frame_to_send = 0
    ack_expected = 0
    frame_expected = 0
    nbuffered = 0

    while (True):
        # 发
        while (not sendFinisfed and nbuffered < MAX_SEQ - 1):
            nbuffered += 1
            packet = CreatPacket(next_frame_to_send, frame_expected, bufferp, buffer, sendFinisfed)
            bufferp += 1
            print("{}, send: pdu_to_send={}, status=New, ackedNo={}".format(sendId,packet.seq, packet.ack))
            sendId+=1
            # packet=pickle.dumps(packet)
            QueueSet[tempport].put(packet)
            next_frame_to_send = (next_frame_to_send + 1) % MAX_SEQ
            if (bufferp >= buffersz):
                sendFinisfed = True
                # next_frame_to_send=-1 #纯ack标志
                break

        # 处理
        # 超时
        if (setTime == True):
            if (time.time() * 1000 - basetime - postTime > Timeout):
                next_frame_to_send = ack_expected
                bufferp -= nbuffered  # 缓冲区指针倒退
                for i in range(0, nbuffered):
                    if (i == 0):
                        setTime = True
                        postTime = time.time() * 1000 - basetime
                    packet = CreatPacket(next_frame_to_send, frame_expected, bufferp, buffer, False)
                    next_frame_to_send = (next_frame_to_send + 1) % MAX_SEQ
                    bufferp += 1
                    print("{}, send: pdu_to_send={}, status=TO, ackedNo={}".format(sendId,packet.seq, packet.ack))
                    sendId+=1
                    QueueSet[tempport].put(packet)

        if (not QueueSet[tempport].empty()):
            isEmpty = 0
            isemptyTimerSet=False


            now = QueueSet[tempport].get()

            if (now.sender == port):  # 要发送的包
                if (setTime == False):
                    # 开启计时器,gobackN时已经打开了计时，此处可能有错
                    postTime = time.time() * 1000 - basetime
                    setTime = True
                if (not RandomDecide(LostRate)):  # 随机丢包
                    clientsocket.sendto(
                        pickle.dumps(now),
                        (socket.gethostbyname(socket.gethostname()), tempport))
                else:
                    print("lost")

            elif (now.sender != port):  # 要接收的包
                if (now.seq == frame_expected):
                    if (not otherhostset): otherhost = now.sender
                    recvId += 1

                    checksum = crc16(now.data)
                    if (checksum != now.checksum):
                        # 校验出错，直接丢弃
                        print("{}, receive: pdu_exp={}, pdu_recv={}, status=DataErr".format(recvId, frame_expected,now.seq))
                    else:
                        print("{}, receive: pdu_exp={}, pdu_recv={}, status=OK".format(recvId,frame_expected, now.seq))
                        recvId+=1
                        frame_expected = (frame_expected + 1) % MAX_SEQ
                        receiver += now.data

                        if (sendFinisfed):  # 发送完毕，回复纯ack
                            packet = CreatPacket(-1, frame_expected, bufferp, buffer, sendFinisfed)
                            QueueSet[tempport].put(packet)

                elif (now.seq == -1):
                    print("receive pure ack {}".format(now.ack))

                else:
                    recvId+=1
                    print(
                        "{}, receive: pdu_exp={}, pdu_recv={}, status=NoErr".format(recvId, frame_expected, now.seq))

                print("before between : ack_expected={},now.ack={},next_frame_to_send={}"
                      .format(ack_expected, now.ack, next_frame_to_send))
                while (between(ack_expected, now.ack, next_frame_to_send)):
                    nbuffered -= 1
                    setTime = False
                    ack_expected = (ack_expected + 1) % MAX_SEQ
        else:
            if (nbuffered == 0): isEmpty += 1
            if(not isemptyTimerSet):
                isemptyTimerSet=True
                emptyTimer=time.time()

        if (isemptyTimerSet and (time.time()-emptyTimer)>3):  # 队列连续为空，认为传输结束
            print('文件接收完成')
            f = open('./host3/receivefrom{}.txt'.format(otherhost), 'wb')
            f.write(receiver)
            break


def main():

    localsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    host = socket.gethostbyname(socket.gethostname())
    localsocket.bind((host, port))
    localsocket.setblocking(0)

    targetaddr = (socket.gethostbyname(socket.gethostname()), int(sys.argv[1]))
    Receive(localsocket, sys.argv[2],targetaddr)

if __name__ == '__main__':
    main()
