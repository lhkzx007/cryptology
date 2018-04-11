# 基于socket传递消息
import queue
import socket
import threading  # 线程类

import pickle


class MessagePump(threading.Thread):
    class MPHelper(threading.Thread):  # 封装消息传递
        def __init__(self, owner):
            """
            接收消息,并将消息放入 queue消息列队中
            :param owner: 所属者
            """
            self.owner = owner
            threading.Thread.__init__(self)  # 初始化父类

        def run(self):
            while not self.owner.abort:  # 只要所有者线程没结束
                try:
                    # 返回二进制数据,返回地址
                    (bytes, addr) = self.owner.socket.recvfrom(2048)  # 收取消息
                    msg = pickle.loads(bytes,encoding="bytes")
                    msg.addr = addr[1]  # 取出地址
                    self.owner.queue.put(msg)  # 存入消息队列
                except Exception as e:
                    print(e)

    def __init__(self, owner, port, timeout=3):
        """
        消息处理类
        :param owner:   消息所有者
        :param port:    消息的端口
        :param timeout: 消息超时时间
        """
        threading.Thread.__init__(self)
        self.owner = owner  # 所有者
        self.abort = False
        self.timeout = timeout  # 超时时间
        self.port = port  # 端口
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP通信
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 200000)
        self.socket.bind(("127.0.0.1", port))  # 通信地址绑定
        self.socket.settimeout(self.timeout)  # 设置连接超时
        self.queue = queue.Queue()  # 创建消息队列
        self.helper = MessagePump.MPHelper(self)  # 接收消息
        pass

    def run(self):  # 线程运行
        self.helper.start()  # 开启收消息的线程
        while not self.abort:
            message = self.waitForMessage()  # 阻塞等待消息
            self.owner.recvMessage(message)  # 收取消息

    def waitForMessage(self):  # 等待消息
        msg = None
        try:
            msg = self.queue.get(True, 3)  # 抓取数据,最多等3秒
        except Exception as e:
            print(e)
        return msg

    def sendMessage(self, message):  # 发送消息
        bytes = pickle.dumps(message)  # 消息转化为二进制
        address = ("127.0.0.1", message.to)  # 地址ip,端口
        self.socket.sendto(bytes, address)  # 发送消息
        return True

    def doAbort(self):  # 设置线程可结束
        self.abort = True
