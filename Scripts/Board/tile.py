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

    def get_init_edges_around_tile(self):
        vertex_offset = self.vertices[1:] + [self.vertices[0]]
        edges_around_tile = self.get_init_edges_from_vertex_offset(
            vertex_offset)
        return edges_around_tile

    def get_init_edges_from_vertex_offset(self, vertex_offset):
        edges_around_tile = [
            Edge(self.board, vertex_1, vertex_2)
            for vertex_1, vertex_2 in zip(self.vertices, vertex_offset)]
        return edges_around_tile

    def get_edges_around_tile(self):
        edges_neighbouring_tile = self.get_edges_neighbouring_tile()
        midpoint_vectors = self.get_midpoint_vectors(edges_neighbouring_tile)
        angles = np.arctan2(*midpoint_vectors.T)
        order = angles.argsort()[[3, 2, 1, 0, 5, 4]]
        edges_around_tile = edges_neighbouring_tile[order]
        return edges_around_tile

    def get_midpoint_vectors(self, edges_neighbouring_tile):
        vectors_to_midpoints = np.array([
            edge.get_midpoint() - self.vector
            for edge in edges_neighbouring_tile])
        return vectors_to_midpoints

    def get_edges_neighbouring_tile(self):
        edges_neigbouring_tile = np.array([
            edge for edge in self.board.edges
            if (edge.vertices[0] in self.vertices and
                edge.vertices[1] in self.vertices)])
        return edges_neigbouring_tile

