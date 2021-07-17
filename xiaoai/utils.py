import random
import string


def generate_random_str(length: int, is_digit: bool = False):
    """
    生成随机字符串
    :param length:
    :param is_digit:
    :return:
    """
    if is_digit:
        all_char = string.digits
    else:
        all_char = string.ascii_letters + string.digits
    return "".join(random.sample(all_char, length))
