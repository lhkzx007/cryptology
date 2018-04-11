# 消息传递类

class Message:
    MSG_ACCEPTOR_AGREE = 0  # 追随者约定
    MSG_ACCEPTOR_ACCEPT = 1  # 追随者接受
    MSG_ACCEPTOR_REJECT = 2  # 追随者拒绝 (消息未响应)
    MSG_ACCEPTOR_UNACCEPT = 3  # 追随者不同意 
    MSG_ACCEPT = 4  # 同意
    MSG_PROPOSE = 5  # 提议
    MSG_EXT_PROPOSE = 6  # 额外提议
    MSG_HEARTBEAT = 7  # 心跳同步消息

    def __init__(self, command=None):
        self.command = command
        self.proposalID = None  # 提议id
        self.instanceId = None  # 当前id
        self.to = None  # 接受者
        self.source = None  # 发送者
        self.value = None  # 消息内容

    def copyAsReply(self, message):
        self.proposalID = message.proposalID  # 提议id
        self.instanceId = message.instanceId  # 当前id
        self.to = message.to  # 接受者
        self.source = message.source  # 发送者
        self.value = message.value  # 消息内容
