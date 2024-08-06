from catan import Catan

catan = Catan()
#catan.board.generate_layout("TestLayout")
catan.board.load_layout("TestLayout")
catan.board.plot_tiles()
