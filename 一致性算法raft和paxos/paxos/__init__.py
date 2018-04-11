import queue
import socket
import threading
import pickle

import time

from paxos.Message import Message
from paxos.MessagePump import MessagePump
from paxos.PaxosAcceptor import PaxosAcceptor
from paxos.PaxosAcceptorProtocol import PaxosAcceptorProtocol
from paxos.PaxosLeader import PaxosLeader
from paxos.PaxosLeaderProtocol import PaxosLeaderProtocol

if __name__ == "__main__":
    # 设定5个客户端
    numclinents = 5
    clients = [PaxosAcceptor(port, [54321, 54322]) for port in range(64320, 64320 + numclinents)]
    # 创建2个领导者
    leader1 = PaxosLeader(54321, [54322], [c.port for c in clients])
    leader2 = PaxosLeader(54322, [54321], [c.port for c in clients])

    leader1.setPrimary(True)
    leader2.setPrimary(True)

    leader1.start()
    leader2.start()

    for c in clients:
        c.start()

    # 假设一个客户端不链接
    clients[0].fail()
    clients[2].fail()

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    start = time.time()
    for i in range(1000):
        msg = Message(Message.MSG_EXT_PROPOSE)
        msg.value = 0 + i
        msg.to = 54322  # 设置传递的端口
        b = pickle.dumps(msg)  # 二进制数据
        s.sendto(b, ("127.0.0.1", msg.to))

    while leader2.getNumAccepted() < 999:
        print("休眠的这一秒 %d " % leader2.getNumAccepted())
        time.sleep(1)

    print(u"休眠10秒")
    time.sleep(10)
    print(u"停止leaders")
    leader1.stop()
    leader2.stop()
    print(u"休眠10秒")
    for c in clients:
        c.stop()

    print(u"leader1历史记录")
    print((leader1.getHistory()))
    print(u"leader2历史记录")
    print((leader2.getHistory()))

    end = time.time()
    print(u"一共用了%f秒" % (end - start))
