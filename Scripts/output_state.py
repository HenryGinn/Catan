import matplotlib.pyplot as plt
import numpy as np

from Players.player_perspective import PlayerPerspective
from global_variables import state_indexes


x_values_all = {
    "Sheep": np.arange(19),
    "Ore": np.arange(19),
    "Mud": np.arange(19),
    "Wood": np.arange(19),
    "Wheat": np.arange(19),
    "Monopoly": np.arange(3),
    "Road Builder": np.arange(3),
    "Year of Plenty": np.arange(3),
    "Victory": np.arange(6),
    "Unplayed Knight": np.arange(11),
    "Played Knight": np.arange(11)}

x_ticks_all = {
    "Sheep": np.array([0, 5, 10, 15]),
    "Ore": np.array([0, 5, 10, 15]),
    "Mud": np.array([0, 5, 10, 15]),
    "Wood": np.array([0, 5, 10, 15]),
    "Wheat": np.array([0, 5, 10, 15]),
    "Monopoly": np.array([0, 1, 2]),
    "Road Builder": np.array([0, 1, 2]),
    "Year of Plenty": np.array([0, 1, 2]),
    "Victory": np.array([0, 1, 2, 3, 4, 5]),
    "Unplayed Knight": np.array([0, 2, 4, 6, 8, 10]),
    "Played Knight": np.array([0, 2, 4, 6, 8, 10])}

w_space = 0
h_space = 0.12
bottom = 0.07
top = 0.12
left = 0.05
right = 0.03
allocated_width = 1 - left - right
allocated_height = (1 - top - bottom - h_space) / 2
width_resource = allocated_width / 5

axes_1_args = [bottom + allocated_height + h_space, width_resource, allocated_height]
axes_2_args = [bottom, width_resource, allocated_height]

ax1_left = left
ax2_left = ax1_left + width_resource
ax3_left = ax2_left + width_resource
ax4_left = ax3_left + width_resource
ax5_left = ax4_left + width_resource

axes_2_widths = np.array([15, 15, 15, 20, 30, 30])
axes_2_widths = allocated_width * axes_2_widths / np.sum(axes_2_widths)
axes_2_lefts = np.cumsum(np.concat(([left], axes_2_widths)))

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
    fig = plt.figure(figsize=(15, 10))
    axes_1 = get_axes_1(fig)
    axes_2 = get_axes_2(fig)
    axes = axes_1 + axes_2
    remove_ticks(axes)
    return fig, axes

def get_axes_1(fig):
    ax1 = fig.add_axes([ax1_left, *axes_1_args])
    ax2 = fig.add_axes([ax2_left, *axes_1_args], sharey=ax1)
    ax3 = fig.add_axes([ax3_left, *axes_1_args], sharey=ax1)
    ax4 = fig.add_axes([ax4_left, *axes_1_args], sharey=ax1)
    ax5 = fig.add_axes([ax5_left, *axes_1_args], sharey=ax1)
    axes_1 = [ax1, ax2, ax3, ax4, ax5]
    return axes_1

def get_axes_2(fig):
    axes_2 = [
        fig.add_axes([axes_2_left, bottom, axes_2_width, allocated_height])
        for axes_2_left, axes_2_width in zip(axes_2_lefts, axes_2_widths)]
    return axes_2

def remove_ticks(axes):
    for index, ax in enumerate(axes):
        if index not in [0, 5]:
            ax.tick_params("y", labelleft=False)

def plot_data(card_state, fig, axes):
    for ax, (card_type, slicer) in zip(axes, state_indexes.items()):
        x_values = x_values_all[card_type]
        distribution = card_state[slicer]
        ax.bar(x_values, distribution, width=1, align="center")
        ax.set_xticks(x_ticks_all[card_type])
        ax.set_title(card_type, fontsize=14)

def plot_peripherals(perspective_name, fig):
    if perspective_name is not None:
        title = f"Card State For {perspective_name}"
        fig.suptitle(title, fontsize=18, y=0.98)


if __name__ == "__main__":
    from global_variables import initial_state
    fig, axes = plot_card_state(initial_state)
