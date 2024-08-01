from os.path import join
from json import load

import numpy as np

from vertex import Vertex


class Board():

    def __init__(self, catan):
        self.catan = catan
        self.initialise_vertices()

    def initialise_vertices(self):
        vertex_vectors = self.get_vertex_position_vectors()
        self.vertices = [Vertex(position_vector)
                         for position_vector in vertex_vectors]
        self.set_verticies_neighbours(vertex_vectors)
        self.set_vertex_positions()

    def get_vertex_position_vectors(self):
        path = join(self.catan.path_resources, "Vertex Positions.json")
        with open(path, "r") as file:
            vertex_vectors = np.array(load(file))
        return vertex_vectors

    def set_verticies_neighbours(self, vertex_vectors):
        directions = np.array([[1, 0], [0, 1], [-1, 1],
                               [-1, 0], [0, -1], [1, -1]])
        for vertex in self.vertices:
            self.set_vertex_neighbours(vertex, directions, vertex_vectors)

    def set_vertex_neighbours(self, vertex, directions, vertex_vectors):
        possible_neighbours = np.array([vertex.vector + [i, j]
                                        for (i, j) in directions])
        matching_values = (vertex_vectors[:, None] == possible_neighbours)
        neighbours = np.where(matching_values.all(axis=2))[0]
        vertex.neighbours = [self.vertices[index] for index in neighbours]

    def set_vertex_positions(self):
        for vertex in self.vertices:
            vertex.set_position()
