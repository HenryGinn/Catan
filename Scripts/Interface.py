from catan import Catan

catan = Catan("TestGame")
#catan.board.input_layout("TestLayout")
#catan.board.generate_layout("TestLayout")
#catan.board.load_layout("TestLayout")
#catan.board.plot_layout()
#catan.initialise_players(names=["H", "Y", "D", "J"],
#                         colours=["blue", "green", "red", "yellow"])
#catan.set_initial_states()
#catan.save()
catan.load()
#catan.set_player_colours()
a = catan.players[0]
catan.board.plot_state()
