# 领导者协议
from paxos.Message import Message
from paxos.MessagePump import MessagePump


class PaxosLeaderProtocol:
    STATE_UNDEFINED = -1  # 协议未定义
    STATE_PROPOSED = 0  # 协议消息
    STATE_REJECTED = 1  # 拒绝链接
    STATE_AGREED = 2  # 同意链接
    STATE_ACCEPTED = 3  # 同意请求
    STATE_UNACCEPTED = 4  # 拒绝请求

    def __init__(self, leader):
        self.leader = leader
        self.state = PaxosLeaderProtocol.STATE_UNDEFINED
        self.proposalID = (-1, -1)  # 初始化,网络好坏的情况
        self.argreecount, self.acceptcount = (0, 0)
        self.rejectcount, self.unacceptcount = (0, 0)
        self.instanceID = -1
        self.highestseen = (0, 0)  # 最高协议

    def propose(self, value, pID, instaceID):  # 提议
        self.proposalID = pID
        self.value = value
        self.instanceID = instaceID  # 初始化id
        # 创建消息
        message = Message(Message.MSG_PROPOSE)  # 提议消息
        message.proposalID = pID
        message.instanceId = instaceID
        message.value = value

        for server in self.leader.getAcceptors():
            message.to = server
            self.leader.sendMessage(message)
        self.state = PaxosLeaderProtocol.STATE_PROPOSED
        return self.proposalID

    def doTranition(self, message):  # 过渡
        # 根据状态机一举拿下协议
        if self.state == PaxosLeaderProtocol.STATE_PROPOSED:
            if message.command == Message.MSG_ACCEPTOR_ACCEPT:  # 同意协议
                self.argreecount += 1
                if self.argreecount > self.leader.getQuorunSize():  # 选举
                    self.state = PaxosLeaderProtocol.STATE_ACCEPTED  # 同意更新
                    if message.value is not None:
                        if message.sequence[0] >= self.highestseen[0] and \
                                        message.sequence[1] > self.highestseen[1]:
                            self.value = message.value
                            self.highestseen = message.sequence

                    # 发送同意消息
                    msg = Message(Message.MSG_ACCEPT)
                    msg.copyAsReply(message)
                    msg.value = self.value
                    msg.leaderID = self.to
                    for server in self.leader.getAcceptors:
                        msg.to = server
                        self.leader.sendMessage(msg)
                    self.leader.notifyLeader(self, message)
                return True
            elif message.command == Message.MSG_ACCEPTOR_REJECT:
                self.rejectcount += 1
                if self.rejectcount >= self.leader.getQuorunSize:
                    self.state = PaxosLeaderProtocol.STATE_REJECTED
                    self.leader.notifyLeader(self, message)
                return True

        elif self.state == PaxosLeaderProtocol.STATE_ACCEPTED:
            if message.command == Message.MSG_ACCEPTOR_ACCEPT:  # 同意协议
                self.acceptcount += 1
                if self.acceptcount > self.leader.getQuorunSize():
                    self.state = PaxosLeaderProtocol.STATE_ACCEPTED
                    self.leader.notifyLeader(self, message)
            elif message.command == Message.MSG_ACCEPTOR_UNACCEPT:  # 不同意
                self.unacceptcount += 1
                if self.unacceptcount > self.leader.getQuorunSize():  # 投票
                    self.state = PaxosLeaderProtocol.STATE_UNACCEPTED
                    self.leader.notifyLeader(self, message)
