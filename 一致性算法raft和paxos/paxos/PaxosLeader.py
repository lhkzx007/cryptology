# 领导者
import queue
import threading

import time

from paxos.InstanceRecord import InstanceRecord
from paxos.Message import Message
from paxos.MessagePump import MessagePump
from paxos.PaxosLeaderProtocol import PaxosLeaderProtocol


class PaxosLeader:
    # 定时监听
    class HeartbeatListener(threading.Thread):
        def __init__(self, leader):
            self.leader = leader  # 领导者
            self.queue = queue.Queue()  # 队列
            self.abort = False
            threading.Thread.__init__(self)

        def newHB(self, message):  # 插入数据
            self.queue.put(message)

        def doAbort(self):  # 停止线程
            self.abort = True

        def run(self):  # 开始执行,读取消息
            elapsed = 0  # 时间计数器
            while not self.abort:
                times = time.time()
                try:
                    hb = self.queue.get(True, 2)  # 抓取消息
                    # 设定规则,假设谁的端口号比较高谁是领导
                    if hb.source > self.leader.port:
                        self.leader.setPrimary(False)
                except Exception as e:
                    self.leader.setPrimary(True)

            pass

    # 定时发送
    class HeartbeatSender(threading.Thread):
        def __init__(self, leader):
            self.leader = leader
            self.abort = False
            threading.Thread.__init__(self)

        def doAbort(self):
            self.abort = True

        def run(self):
            while not self.abort:
                time.sleep(1)
                if self.leader.isPrimary:
                    msg = Message(Message.MSG_HEARTBEAT)
                    msg.source = self.leader.port
                    for leader in self.leader.leaders:  # 循环遍历领导者,发送信息
                        msg.to = 1
                        self.leader.sendMessage(msg)  # 发送消息

    def __init__(self, port, leaders=None, acceptors=None):
        self.port = port
        if leaders is None:
            self.leaders = []
        else:
            self.leaders = leaders
        if acceptors is None:
            self.acceptors = []
        else:
            self.acceptors = acceptors

        self.group = self.leaders + self.acceptors
        self.isPrimary = False
        self.proposalcount = 0
        self.msgPump = MessagePump(self, port)  # 消息传送器
        self.instances = {}
        self.hbListener = PaxosLeader.HeartbeatListener(self)  # 监听心跳
        self.hbSender = PaxosLeader.HeartbeatSender(self)  # 发送
        self.highestInstance = -1  # 协议状态
        self.stoped = True  # 是否正在运行
        self.lasttime = time.time()  # 最后一次的时间

    def sendMessage(self, message):  # 发送消息
        self.msgPump.sendMessage(message)

    def start(self):  # 开始
        """
        启动
        :return:
        """
        self.hbSender.start()
        self.hbListener.start()
        self.msgPump.start()
        self.stoped = False

    def stop(self):  # 停止
        self.hbSender.doAbort()
        self.hbListener.doAbort()
        self.msgPump.doAbort()
        self.stoped = False

    def setPrimary(self, primary):  # 设置领导者
        if self.isPrimary is not primary:
            self.isPrimary = primary
            print(" isPrimary", primary)

    def getGroup(self):  # 获取所有的领导者的追随者
        return self.group

    def getLeaders(self):  # 获取所有的领导
        return self.leaders

    def getAcceptors(self):  # 获取所有的追随者
        return self.acceptors

    def getQuorunSize(self):  # 必须活着 51% 的支持
        return (len(self.getAcceptors()) / 2) + 1

    def getInstanceValue(self, instanceID):  # 获取接口数据
        if instanceID in self.instances:
            return self.instances[instanceID].value
        return None

    def getHistory(self):  # 抓取的历史记录
        return [self.getInstanceValue(i) for i in range(1, self.highestInstance + 1)]

    def getNumAccepted(self):  # 获取同意的数量
        return len([v for v in self.getHistory() if v is not None])

    def garbageCollect(self):  # 采集无用信息
        for i in self.instances:
            self.instances[i].cleanProtocol()

    def findAndFillGaps(self):  # 抓取空白时间处理事务
        for i in range(1, self.highestInstance):
            if self.getInstanceValue(i) is None:
                print("填充空白", i)
                self.newProposal(0, i)
        self.lasttime = time.time()

    def notifyLeader(self, protocol, message):  # 通知领导
        if protocol.state == PaxosLeaderProtocol.STATE_ACCEPTED:
            print("协议接口%s 被%s接收" % (message.instanceId, message.value))
            self.instances[message.instanceId].accepted = True
            self.instances[message.instanceId].value = message.value
            self.highestInstance = max(message.instanceId, self.highestInstance)
            return
        if protocol.state == PaxosLeaderProtocol.STATE_REJECTED:
            self.proposalcount = max(message.highestPID[1], self.proposalcount)
            self.newProposal(message.value)
            return
        if protocol.state == PaxosLeaderProtocol.STATE_REJECTED:
            pass

    def newProposal(self, value, instacnce=None):  # 新的提议
        protocol = PaxosLeaderProtocol(self)
        if instacnce is None:
            self.highestInstance += 1
            instacnceID = self.highestInstance
        else:
            instacnceID = self.highestInstance
        self.proposalcount += 1  # 协议追加
        id = (self.port, self.proposalcount)
        if instacnceID in self.instances:
            record = self.instances[instacnceID]
        else:
            record = InstanceRecord()
            self.instances[instacnceID] = record
        protocol.propose(value, id, instacnceID)  # 记录
        record.addProtocol(protocol)  # 追加协议

    def recvMessage(self, message):  # 接收数据
        if self.stoped:
            return
        if message is None:
            if self.isPrimary and time.time() - self.lasttime > 15.0:
                self.findAndFillGaps()
                self.garbageCollect()
            return
        if message.command == Message.MSG_HEARTBEAT:  # 处理心跳消息
            self.hbListener.newHB(message)
            return True

        if message.command == Message.MSG_EXT_PROPOSE:
            print("额外的协议 ", self.port, self.highestInstance)
            if self.isPrimary:
                self.newProposal(message.value)

            return True
        if self.isPrimary and message.command != Message.MSG_ACCEPTOR_ACCEPT:
            self.instances[message.instanceId].getProtocol(message.proposalID).doTranition()

        if message.command == Message.MSG_ACCEPTOR_ACCEPT:
            if message.instanceId not in self.instances:
                self.instances[message.instanceId] = InstanceRecord()
            record = self.instances[message.instanceId]
            if message.proposalID not in record:  # 创建新的协议
                protocol = PaxosLeaderProtocol(self)
                protocol.state = PaxosLeaderProtocol.STATE_ACCEPTED
                protocol.proposalID = message.proposalID
                protocol.instanceID = message.instanceId
                protocol.value = message.value
                record.addProtocol(protocol)
            else:  # 取出协议
                protocol = record.getProtocol(message.proposalID)

            protocol.doTranition()

        return True
