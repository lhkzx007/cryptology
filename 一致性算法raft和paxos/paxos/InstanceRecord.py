# InstanceRecord 本地记录类,follower追随者 与 leader领导者的协议
from paxos.PaxosLeaderProtocol import PaxosLeaderProtocol


class InstanceRecord:
    def __init__(self):
        self.protocols = {}
        self.highestId = (-1, 1)
        self.value = None

    # 添加协议
    def addProtocol(self, protocol):
        self.protocols[protocol.proposalID] = protocol
        # 取得编号最多的协议
        if protocol.proposalID[1] >= self.highestId[1] \
                and protocol.proposalID[0] > self.highestId[0]:
            self.highestId = protocol.proposalID

    # 根据编号,抓取协议
    def getProtocol(self, proposalID):
        return self.protocols[proposalID]

    def cleanProtocol(self):  # 清理协议
        # self.protocols.clear()
        keys = self.protocols.keys()
        for key in keys:
            protocol = self.protocols[key]
            if protocol.state == PaxosLeaderProtocol.STATE_ACCEPTED:
                del self.protocols[key]
