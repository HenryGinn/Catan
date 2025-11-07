import os

from numpy import array


path_base = os.path.dirname(os.path.dirname(__file__))
path_data = os.path.join(path_base, "Data")
path_resources = os.path.join(path_data, "Resources")
path_layouts = os.path.join(path_data, "Layouts")

real_estate = {
    "Settlements": "Vertex",
    "Cities": "Vertex",
    "Roads": "Edge"}

initial_state = {
    "Sheep": array([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
    "Ore": array([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
    "Mud": array([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
    "Wood": array([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
    "Wheat": array([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
    "Road Builder": array([1, 0, 0]),
    "Year of Plenty": array([1, 0, 0]),
    "Monopoly": array([1, 0, 0]),
    "Victory": array([1, 0, 0, 0, 0, 0]),
    "Unplayed Knight": array([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
    "Played Knight": array([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])}

card_types = list(initial_state.keys())
resource_types = [
    "Sheep", "Ore", "Mud", "Wood", "Wheat"]
