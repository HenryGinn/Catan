class Edge():

    def __init__(self, board, vertex_1, vertex_2):
        self.board = board
        self.vertices = [vertex_1, vertex_2]

    def get_vectors(self):
        vectors = [(vertex.vector) for vertex in self.vertices]
        return vectors

    def get_midpoint(self):
        midpoint = tuple(
            (i + j) / 2 for i, j in zip(*self.get_vectors()))
        return midpoint
