import matplotlib.pyplot as plt
import numpy as np

from Players.player_perspective import PlayerPerspective
from global_variables import state_indexes


w_space = 0.07
h_space = 0.12
bottom = 0.07
top = 0.12
left = 0.07
right = 0.05
width = (1 - w_space * 2 - left - right) / 3
height = (1 - h_space - top - bottom) / 2

x_values = np.arange(19) + 0.5

def plot_card_state(arg):
    card_state, perspective_name = parse_arg(arg)
    fig, axes = init_figure()
    plot_data(card_state, fig, axes)
    plot_peripherals(perspective_name, fig)
    plt.show()
    return fig, axes

# Expects either a player perspective or a state.
def parse_arg(arg):
    if isinstance(arg, PlayerPerspective):
        return arg.card_state, arg.name
    else:
        return arg, None

def init_figure():
    fig = plt.figure(figsize=(10, 6))
    ax1 = fig.add_axes([left + (width + w_space)*0, bottom + height + h_space, width, height])
    ax2 = fig.add_axes([left + (width + w_space)*1, bottom + height + h_space, width, height])
    ax3 = fig.add_axes([left + (width + w_space)*2, bottom + height + h_space, width, height])
    ax4 = fig.add_axes([left + width*0.7, bottom, width, height])
    ax5 = fig.add_axes([left + width*1.7 + h_space, bottom, width, height])
    axes = [ax1, ax2, ax3, ax4, ax5]
    return fig, axes

def plot_data(card_state, fig, axes):
    for ax, (card_type, slicer) in zip(axes, state_indexes.items()):
        distribution = card_state[slicer]
        ax.bar(x_values, distribution)
        ax.set_title(card_type, fontsize=14)

def plot_peripherals(perspective_name, fig):
    if perspective_name is not None:
        title = f"Card State For {perspective_name}"
        fig.suptitle(title, fontsize=18)


if __name__ == "__main__":
    pass
