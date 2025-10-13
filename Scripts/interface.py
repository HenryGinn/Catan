from hgutilities.utils import json

from catan import Catan

catan = Catan("TestGame")
#catan.board.input_layout("TestLayout")
#catan.board.generate_layout("TestLayout")
catan.board.load_layout("TestLayout")
#catan.board.plot_layout()
#catan.start_game(
#    names=["H", "Y", "D", "J"],
#    colors=["blue", "green", "red", "yellow"])
#catan.save()
catan.load()
#catan.board.plot_state()

a = catan.players[0]
catan.next_turn()
catan.take_turn()
