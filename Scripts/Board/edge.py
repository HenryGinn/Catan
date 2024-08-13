class Edge():

    def __init__(self, board, vertex_1, vertex_2):
        self.board = board
        self.vertices = sorted([vertex_1, vertex_2],
                               key=lambda x: x.ID)
