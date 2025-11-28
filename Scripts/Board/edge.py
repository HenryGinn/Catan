from numpy import array


class Edge():

    def __init__(self, board, vertex_1, vertex_2):
        self.board = board
        self.set_vertices(vertex_1, vertex_2)
        self.update_vertex_edges()

    def set_vertices(self, vertex_1, vertex_2):
        if vertex_1.ID < vertex_2.ID:
            self.vertices = [vertex_1, vertex_2]
        else:
            self.vertices = [vertex_2, vertex_1]

    def update_vertex_edges(self):
        for vertex in self.vertices:
            vertex.edges.append(self)

    def get_vectors(self):
        vectors = [(vertex.vector) for vertex in self.vertices]
        return vectors

    def get_midpoint(self):
        midpoint = array([
            (i + j) / 2 for i, j in zip(*self.get_vectors())])
        return midpoint
