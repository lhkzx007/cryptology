# 追随者 follower
from paxos.Message import Message
from paxos.MessagePump import MessagePump
from paxos.InstanceRecord import InstanceRecord
from paxos.PaxosAcceptorProtocol import PaxosAcceptorProtocol


class PaxosAcceptor:
    def __init__(self, port, leaders):
        self.port = port
        self.leaders = leaders
        self.instances = {}
        self.msgPump = MessagePump(self, self.port)  # 消息传送器
        self.failed = False

    def start(self):  # 开始
        self.msgPump.start()

    def stop(self):  # 停止
        self.msgPump.doAbort()

    def fail(self):  # 失败
        self.failed = True

    def recover(self):  # 恢复
        self.failed = True

    def sendMessage(self, message):  # 发送消息
        self.msgPump.sendMessage(message)

    def recvMessage(self, message):  # 收取消息
        if message is None or self.failed:
            return

        if message.command == Message.MSG_PROPOSE:
            if message.instanceId not in self.instances:
                record = InstanceRecord()
                self.instances[message.instanceId] = record
            protocal = PaxosAcceptorProtocol(self)
            protocal.recvProposal(message)  # 收取消息
            self.instances[message.instanceId].addProtocol(protocal)  # 记录协议
        else:
            self.instances[message.instanceId].getProtocol(message.proposalID)  # 抓取记录

    def notifyChlient(self, protocol, message):  # 通知客户端
        if protocol.state == PaxosAcceptorProtocol.STATE_PROPOSAL_ACCEPTED:
            self.instances[protocol.instanceId].value = message.value
            print("协议被客户端接受")
        pass

    def getInstanceValue(self, instance):  # 获取接口数据
        return self.instances[instance].value

    def getHighestAgreedProposal(self, instance):  # 获取最高同意的建议
        return self.instances[instance].highestId
