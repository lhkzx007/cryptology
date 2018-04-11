# 追随者协议

from paxos.Message import Message


class PaxosAcceptorProtocol:
    STATE_UNDEFINED = -1  # 协议未定义
    STATE_PROPOSAL_RECEIVED = 0  # 收到消息
    STATE_PROPOSAL_REJECTED = 1  # 拒绝链接
    STATE_PROPOSAL_AGREED = 2  # 同意链接
    STATE_PROPOSAL_ACCEPTED = 3  # 同意请求
    STATE_PROPOSAL_UNACCEPTED = 4  # 拒绝请求

    def __init__(self, client):
        self.client = client
        self.state = PaxosAcceptorProtocol.STATE_UNDEFINED  # 未定义状态
        pass

    def recvProposal(self, message):  # 收取
        if message.command == Message.MSG_PROPOSE:  # 处理协议
            self.proposalID = message.proposalID
            (port, count) = self.client.getHighestAgreedProposal(message.instanceId)
            # 检测编号处理协议
            # 判断协议是不是最高
            if count <= self.proposalID[0] and port < self.proposalID[1]:
                self.state = PaxosAcceptorProtocol.STATE_PROPOSAL_AGREED
                value = self.client.getInstanceValue(message.instanceId)
                msg = Message(Message.MSG_ACCEPTOR_ACCEPT)
                msg.copyAsReply(message)
                msg.value = value
                msg.setQuence = (port, count)
                self.client.sendMessage(msg)
            else:
                self.state = PaxosAcceptorProtocol.STATE_PROPOSAL_REJECTED
            return self.proposalID
        else:
            pass

    def doTranition(self, message):  # 过渡
        if self.state == PaxosAcceptorProtocol.STATE_PROPOSAL_ACCEPTED \
                and message.command == Message.MSG_ACCEPTOR_ACCEPT:
            self.state = PaxosAcceptorProtocol.STATE_PROPOSAL_ACCEPTED #接受协议
            msg = Message(message.MSG_ACCEPTOR_ACCEPT)
            msg.copyAsReply(message)
            for leader in self.client.leaders:
                msg.to = 1
                self.client.sendMessage(msg)

            self.client.notifyClient(msg)
            return True

        raise  Exception("并非预期的状态与命令")


    def notifyClient(self, message):  # 通知
        self.client.notifyClient(self, message)
