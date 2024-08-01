from os.path import join
from json import load
from random import shuffle

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

from vertex import Vertex
from tile import Tile


class Board():

    basis = np.array([[0, 1], [np.sin(np.pi/3), np.cos(np.pi/3)]])
    directions = np.array([[1, 0], [0, 1], [-1, 1],
                           [-1, 0], [0, -1], [1, -1]])

    def __init__(self, catan):
        self.catan = catan
        self.load_tile_data()
        self.initialise_vertices()
        self.initialise_tiles()

    def load_tile_data(self):
        path = join(self.catan.path_resources, "Tile Definitions.json")
        with open(path, "r") as file:
            self.tile_data = load(file)

    def initialise_vertices(self):
        vertex_vectors = self.get_vertex_position_vectors()
        self.vertices = [Vertex(self, position_vector)
                         for position_vector in vertex_vectors]
        self.set_verticies_neighbours(vertex_vectors)
        self.set_vertex_positions()

    def get_vertex_position_vectors(self):
        path = join(self.catan.path_resources, "Vertex Positions.json")
        with open(path, "r") as file:
            vertex_vectors = np.array(load(file), dtype="int8")
        return vertex_vectors

    def set_verticies_neighbours(self, vertex_vectors):
        for vertex in self.vertices:
            self.set_vertex_neighbours(vertex, vertex_vectors)

    def set_vertex_neighbours(self, vertex, vertex_vectors):
        possible_neighbours = np.array([vertex.vector + [i, j]
                                        for (i, j) in self.directions])
        matching_values = (vertex_vectors[:, None] == possible_neighbours)
        neighbours = np.where(matching_values.all(axis=2))[0]
        vertex.neighbours = [self.vertices[index] for index in neighbours]

    def set_vertex_positions(self):
        for vertex in self.vertices:
            vertex.set_position()

    def initialise_tiles(self):
        tile_vectors = self.get_tile_centre_position_vectors()
        self.tiles = [self.get_tile(tile_vector)
                      for tile_vector in tile_vectors]

    def get_tile_centre_position_vectors(self):
        path = join(self.catan.path_resources, "Tile Centres.json")
        with open(path, "r") as file:
            tile_vectors = np.array(load(file), dtype="int8")
        return tile_vectors

    def get_tile(self, tile_vector):
        neighbours = tile_vector + self.directions
        vertices = [vertex for neighbour in neighbours
                    for vertex in self.vertices
                    if np.all(vertex.vector == neighbour)]
        tile = Tile(self, tile_vector, vertices)
        return tile

    def plot_tiles(self):
        self.initialise_plot()
        self.add_tiles_to_plot()
        self.set_x_and_y_plot_limits()
        plt.show()

    def initialise_plot(self):
        self.fig, self.ax = plt.subplots(1)
        self.ax.set_aspect('equal')
        self.ax.axis("off")

    def add_tiles_to_plot(self):
        polygons = PatchCollection(
            [Polygon([vertex.position for vertex in tile.vertices],
                     closed=True, facecolor=tile.color, edgecolor="k")
             for tile in self.tiles], match_original=True)
        self.ax.add_collection(polygons)

    def set_x_and_y_plot_limits(self):
        vertex_positions = np.array([vertex.position for vertex in self.vertices])
        min_x, min_y = np.min(vertex_positions, axis=0)*1.1
        max_x, max_y = np.max(vertex_positions, axis=0)*1.1
        self.ax.set_xlim(min_x, max_x)
        self.ax.set_ylim(min_y, max_y)

    def generate_layout(self):
        tile_types = [tile_type for tile_type in self.tile_data
                      for index in range(self.tile_data[tile_type]["Count"])]
        shuffle(tile_types)
        for tile, tile_type in zip(self.tiles, tile_types):
            tile.set_type(tile_type)


























