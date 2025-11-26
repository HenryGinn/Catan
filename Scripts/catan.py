#!.\venv\bin\python3.exe

from hgutilities.utils import json
import numpy as np
import pandas as pd

from game import Game

np.set_printoptions(edgeitems=30, linewidth=10000)

catan = Game("TestGame", reset_log=True, seed=43)
catan.a = None
catan.c = None
#catan.board.input_layout("TestLayout")
#catan.board.generate_layout("TestLayout")
#catan.board.load_layout("TestLayout")
#catan.board.show_layout()
#catan.start_game(
#    names=["H", "Y", "D", "J"],
#    colors=["blue", "green", "red", "yellow"])
#catan.save()
catan.load()
#catan.save_state()

catan.next_turn()
#catan.take_turn()
#catan.buy_road()

a = catan.a
c = catan.c
