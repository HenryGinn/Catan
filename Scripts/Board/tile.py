import numpy as np

from Board.edge import Edge


class Tile():

    def __init__(self, board, tile_data):
        self.board = board
        self.set_vector(tile_data["Vector"])
        self.set_vertices(tile_data["Vertices"])
        self.set_type("Desert")

    def set_vector(self, vector):
        self.vector = tuple(vector)
        self.position = self.board.get_position(self.vector)

    def set_vertices(self, vertex_data):
        self.set_vertex_indicators(vertex_data)
        self.vertices = [
            self.board.vertices[index]
            for index in vertex_data]

    def set_vertex_indicators(self, vertex_data):
        self.vertex_indicators = np.zeros(54)
        self.vertex_indicators[vertex_data] = 1

    def set_type(self, tile_type):
        self.type = tile_type
        self.color = self.board.tile_definitions[tile_type]["Color"]

    def init_edges_around_tile(self):
        vertex_offset = self.vertices[1:] + [self.vertices[0]]
        edges_around_tile = self.init_edges_from_vertex_offset(
            vertex_offset)
        return edges_around_tile

    def init_edges_from_vertex_offset(self, vertex_offset):
        edges_around_tile = [
            Edge(self.board, vertex_1, vertex_2)
            for vertex_1, vertex_2 in zip(self.vertices, vertex_offset)]
        return edges_around_tile

    def get_edges_around_tile(self):
        vertex_offset = self.vertices[1:] + [self.vertices[0]]
        edges_neigbouring_tile = [
            edge for edge in self.board.edges
            if len(edge.vertices.intersect(vertex_offset)) == 2]

