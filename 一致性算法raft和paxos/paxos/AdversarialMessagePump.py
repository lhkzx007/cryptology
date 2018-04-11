import random

from paxos.MessagePump import MessagePump

"""
    Adversarial 对抗
    模拟网络乱序
"""


class AdversarialMessagePump(MessagePump):
    # 对抗消息传输,延迟消息处理 ,模拟网络延时
    def __init__(self, owner, port, timeout=3):
        MessagePump.__init__(owner, port, timeout)
        self.messages = set()  # 避免消息重复

    def waitForMessage(self):  # 等待消息
        msg = None
        try:

            msg = self.queue.get(True, 0.1)  # 抓取数据,最多等0.1秒
            self.messages.add(msg)  # 添加消息
        except Exception as e:
            print(e)

        # 随机处理消息
        if len(self.messages) > 0 and random.random() < 0.95:
            # 随机抓取消息
            msg = random.choice(list(self.messages))
            self.messages.remove(msg)  # 从对
        else:
            msg = None

        return msg
