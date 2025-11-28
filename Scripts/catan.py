#!.\venv\bin\python3.exe

from hgutilities.utils import json
import numpy as np
import pandas as pd

from game import Game

np.set_printoptions(edgeitems=30, linewidth=10000)

catan = Game("TestGame", reset_log=True, seed=43)
catan.a = None
catan.c = None
#catan.input_layout("TestGame2")
#catan.generate_layout("TestLayout")
#catan.load_layout("TestLayout")
#catan.show_layout()
#catan.start_game(
#    names=["H", "Y", "D", "J"],
#    colors=["blue", "green", "red", "yellow"])
#catan.save()
catan.load()
#catan.save_state()

#catan.next_turn()
#catan.take_turn()
catan.buy_road("H", 3, 0, 4)
catan.buy_road("H", None, 0, 0)
catan.buy_road("J", None, 0, 5)
catan.buy_road("J", 11, 0, 0)
catan.buy_road("H", 4, 0, 4)
catan.buy_city("H", 3, 0, 4)
catan.buy_settlement("J", 11, 0, 0)
catan.buy_settlement("J", None, 0, 0)
catan.show_board()
catan.save_board()

a = catan.a
c = catan.c
