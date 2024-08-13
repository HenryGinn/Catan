import time


def get_name(name=None):
    if name is None:
        name = time.strftime("%Y_%M_%d__%H_%M")
    return name
