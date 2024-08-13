from catan import Catan

catan = Catan("TestGame", player_names=["H", "Y", "V", "J"])
#catan.board.input_layout("TestLayout")
#catan.board.generate_layout("TestLayout")
catan.board.load_layout("TestLayout")
#catan.board.plot_tiles()
a = catan.players[0]
catan.set_initial_states()
catan.save()
#catan.load()
