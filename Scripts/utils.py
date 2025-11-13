import time


def get_name(name=None):
    if name is None:
        name = time.strftime("%Y_%M_%d__%H_%M")
    return name

def get_change_str(change):
    change = int(change)
    if change >= 0:
        change_str = f"gained {change}"
    else:
        change_str = f"lost {-change}"
    return change_str
