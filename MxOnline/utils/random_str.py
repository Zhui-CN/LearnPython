import string
from random import choice


def generate_random(random_length, random_type):
    """
    随机字符串生成函数
    :param random_length:字符串长度
    :param random_type:字符串类型（0：纯数字 or 1：数字+字符 or 2：数字+字符+特殊字符）
    :return:生成的随机字符串
    """
    if random_type == 0:
        random_seed = string.digits
    elif random_type == 1:
        random_seed = string.digits + string.ascii_letters
    else:
        random_seed = string.digits + string.ascii_letters + string.punctuation
    return ''.join([choice(random_seed) for _ in range(random_length)])


if __name__ == "__main__":
    print(generate_random(4, 0))
