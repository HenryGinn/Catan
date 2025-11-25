import os

import numpy as np


path_base = os.path.dirname(os.path.dirname(__file__))
path_data = os.path.join(path_base, "Data")
path_resources = os.path.join(path_data, "Resources")
path_layouts = os.path.join(path_data, "Layouts")

real_estates = ["Settlements", "Cities", "Roads"]

real_estate_graph_components = {
    "Settlements": "Vertex",
    "Cities": "Vertex",
    "Roads": "Edge"}

real_estate_sizes = {
    "Settlements": 54,
    "Cities": 54,
    "Roads": 57}

tile_numbers = [
    2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]

card_sizes = {
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
    for card_type, size in card_sizes.items()}
for state in initial_state.values():
    state[0] = 1

card_types = list(initial_state.keys())
resource_types = [
    "Sheep", "Ore", "Mud", "Wood", "Wheat"]
tile_types_list = resource_types + ["Desert"]

sizes = real_estate_sizes | card_sizes

action_columns = card_types + [
    "Trade Partner",
    "Settlement", "City", "Road 1", "Road 2", # Two roads to account for Road Builder
    "Robber", "Robbee", "Robbed Tile",
    "Dumped 1", "Dumped 2", "Dumped 3", "Dumped 4",
    "Gained 1", "Gained 2", # Accounting for ports and Year of Plenty
    "Monopoly"]
