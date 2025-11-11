import os

import numpy as np


path_base = os.path.dirname(os.path.dirname(__file__))
path_data = os.path.join(path_base, "Data")
path_resources = os.path.join(path_data, "Resources")
path_layouts = os.path.join(path_data, "Layouts")

real_estate = {
    "Settlements": "Vertex",
    "Cities": "Vertex",
    "Roads": "Edge"}

tile_numbers = [
    2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]

sizes = {
    "Sheep": 19,
    "Ore": 19,
    "Mud": 19,
    "Wood": 19,
    "Wheat": 19,
    "Road Builder": 3,
    "Year of Plenty": 3,
    "Monopoly": 3,
    "Victory": 6,
    "Unplayed Knight": 11,
    "Played Knight": 11}

initial_state = {
    card_type: np.zeros(size)
    for card_type, size in sizes.items()}
for state in initial_state.values():
    state[0] = 1

card_types = list(initial_state.keys())
resource_types = [
    "Sheep", "Ore", "Mud", "Wood", "Wheat"]
