from hgutilities.utils import json

from catan import Catan

catan = Catan("TestGame")
#catan.board.input_layout("TestLayout")
#catan.board.generate_layout("TestLayout")
#catan.board.load_layout("TestLayout")
#catan.board.plot_layout()
#catan.initialise_players(names=["H", "Y", "D", "J"],
#                         colors=["blue", "green", "red", "yellow"])
#catan.set_initial_states()
catan.load()
a = catan.players[0]
print(a)
#catan.save()
#catan.set_player_colours()
#catan.board.plot_state()
#catan.trade({"H": {"Settlements": [(3, -2)],
#                   "Roads": [(-0.5, 2.5)],
#                   "Wheat": 4, "Wood": 4,
#                   "Mud": 5, "Sheep": 3,
#                   "Development": 2},
#             "J": {"Wood": 4, "Wheat": 2,
#                   "Ore": 3}})
