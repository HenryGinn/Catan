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

tile_numbers = sorted([
    number for number in range(2, 13)
    for weight in range(min(number - 1, 13 - number))])

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

zeros_lookup = {
    card_type: np.zeros(size * 3)
    for card_type, size in sizes.items()}

middle_lookup = {
    card_type: np.arange(size, size * 2)
    for card_type, size in sizes.items()}

arange_lookup = {
    card_type: np.arange(size)
    for card_type, size in sizes.items()}

card_types = list(initial_state.keys())
resource_types = [
    "Sheep", "Ore", "Mud", "Wood", "Wheat"]

# Assumed distributions when states are not normalisable. These should
# not be used and are only included so that the game can continue.
guessed_distributions = {
    "Sheep":            np.array([0.303, 0.251, 0.201, 0.101, 0.030, 0.024, 0.019, 0.015, 0.012, 0.010, 0.008, 0.006, 0.005, 0.004, 0.003, 0.003, 0.002, 0.002, 0.001]),
    "Ore":              np.array([0.303, 0.251, 0.201, 0.101, 0.030, 0.024, 0.019, 0.015, 0.012, 0.010, 0.008, 0.006, 0.005, 0.004, 0.003, 0.003, 0.002, 0.002, 0.001]),
    "Mud":              np.array([0.303, 0.251, 0.201, 0.101, 0.030, 0.024, 0.019, 0.015, 0.012, 0.010, 0.008, 0.006, 0.005, 0.004, 0.003, 0.003, 0.002, 0.002, 0.001]),
    "Wood":             np.array([0.303, 0.251, 0.201, 0.101, 0.030, 0.024, 0.019, 0.015, 0.012, 0.010, 0.008, 0.006, 0.005, 0.004, 0.003, 0.003, 0.002, 0.002, 0.001]),
    "Wheat":            np.array([0.303, 0.251, 0.201, 0.101, 0.030, 0.024, 0.019, 0.015, 0.012, 0.010, 0.008, 0.006, 0.005, 0.004, 0.003, 0.003, 0.002, 0.002, 0.001]),
    "Road Builder":     np.array([0.989, 0.010, 0.001]),
    "Year of Plenty":   np.array([0.989, 0.010, 0.001]),
    "Monopoly":         np.array([0.989, 0.010, 0.001]),
    "Victory":          np.array([0.568, 0.227, 0.114, 0.057, 0.023, 0.011]),
    "Unplayed Knight":  np.array([0.530, 0.396, 0.066, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001]),
    "Played Knight":    np.array([0.530, 0.396, 0.066, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001])}
