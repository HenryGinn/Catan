from catan import Catan

catan = Catan()
#catan.board.input_layout("TestLayout")
#catan.board.generate_layout("TestLayout")
catan.board.load_layout("TestLayout")
#catan.board.plot_tiles()
a = catan.players[0]
catan.set_initial_states()
#catan.players.save()
#catan.players.load()
