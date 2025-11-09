from hgutilities.utils import json
import numpy as np

from game import Game

splash = r"""
      ______     _____    ____________   _____        ____    ___
     /  ___/    /     |  /____   ____/  /     |      /    |  /  /
    /  /       /  /|  |      /  /      /  /|  |     /  /| | /  /
   /  /       /  /_|  |     /  /      /  /_|  |    /  / | |/  /
  /  /       /  ___   |    /  /      /  ___   |   /  /  | |  /
  \  \___   /  /   |  |   /  /      /  /   |  |  /  /   |   /
   \_____/ /__/    |__|  /__/      /__/    |__| /__/    |__/
"""

np.set_printoptions(edgeitems=30, linewidth=10000)

catan = Game("TestGame", reset_log=True, seed=43)
catan.a = None
catan.c = None
#catan.board.input_layout("TestLayout")
#catan.board.generate_layout("TestLayout")
#catan.board.load_layout("TestLayout")
#catan.board.plot_layout()
#catan.start_game(
#    names=["H", "Y", "D", "J"],
#    colors=["blue", "green", "red", "yellow"])
#catan.save()
catan.load()
#catan.board.plot_state()

catan.next_turn()
#catan.take_turn()

a = catan.a
c = catan.c
