from numpy import array

real_estate = {
    "Settlements": "Vertex",
    "Cities": "Vertex",
    "Roads": "Edge"}

state_indexes = {
    "Sheep": slice(None, 19),
    "Ore": slice(19, 38),
    "Mud": slice(38, 57),
    "Wood": slice(57, 76),
    "Wheat": slice(76, 95),
    "Monopoly": slice(95, 98),
    "Road Builder": slice(98, 101),
    "Year of Plenty": slice(101, 104),
    "Victory": slice(104, 110),
    "Unplayed Knight": slice(110, 121),
    "Played Knight": slice(121, None)}

initial_state = array([
    1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

