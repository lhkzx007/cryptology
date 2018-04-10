import numpy as np


# Homomorphic Encryption 同态加密
# 制造key
def makeKey(w, m, n):
    """
    制造一个key
    :param w: 向量
    :param m: 范围
    :param n: 范围
    :return:
    """
    S = np.random.rand(m,n) * w
    return S


def encrypt(x, S, m, n, w):
    """
    加密
    :param x: 消息
    :param S: 秘钥 key
    :param m: 范围
    :param n: 范围
    :param w: 向量
    :return:
    """
    e = np.random.rand(m)
    print(" --e --",e)
    c = np.linalg.inv(S).dot((w * x) + e)
    return c


def decrypt(c, S, w):
    """
    解密
    :param c: 解密的数据
    :param S: 秘钥key
    :param w: 向量
    :return:
    """
    return (S.dot(c) / w).astype("int")


x = np.array([1, 11, 12, 13, 15, 6000])

m = len(x)
n = m
w = 15
S = makeKey(w, m, n)

print(type(S))
c = encrypt(x, S, m, n, w)
print(c)
print(decrypt(c, S, w))

# s*c=wx+e


a = np.arange(1, 6)
b = a[::-1]
print(a, b)
print(a.dot(b))
print(a * 3)
