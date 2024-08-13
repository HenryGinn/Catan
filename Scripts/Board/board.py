from os.path import join
from json import load
from random import shuffle
import json

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

from Board.vertex import Vertex
from Board.tile import Tile
from Board.edge import Edge
from utils import get_name


class Board():

    basis = np.array([[0, 1], [np.sin(np.pi/3), np.cos(np.pi/3)]])
    directions = np.array([[1, 0], [0, 1], [-1, 1],
                           [-1, 0], [0, -1], [1, -1]])

    def __init__(self, catan):
        self.catan = catan
        self.load_tile_data()
        self.initialise_graph_components()

    def load_tile_data(self):
        path = join(self.catan.path_resources, "Tile Definitions.json")
        with open(path, "r") as file:
            self.tile_data = load(file)

    def initialise_graph_components(self):
        self.initialise_vertices()
        self.initialise_tiles()
        self.initialise_edges()


    # Vertices

    def initialise_vertices(self):
        vertex_vectors = self.get_vertex_position_vectors()
        self.vertices = [Vertex(self, position_vector, index)
                         for index, position_vector in
                         enumerate(vertex_vectors)]

    def get_vertex_position_vectors(self):
        path = join(self.catan.path_resources, "Vertex Positions.json")
        with open(path, "r") as file:
            vertex_vectors = np.array(load(file), dtype="int8")
        return vertex_vectors


    # Tiles

    def initialise_tiles(self):
        tile_vectors = self.get_tile_centre_position_vectors()
        self.tiles = [self.get_tile(tile_vector, index)
                      for index, tile_vector in enumerate(tile_vectors)]

    def get_tile_centre_position_vectors(self):
        path = join(self.catan.path_resources, "Tile Centres.json")
        with open(path, "r") as file:
            tile_vectors = np.array(load(file), dtype="int8")
        return tile_vectors

    def get_tile(self, tile_vector, index):
        neighbours = tile_vector + self.directions
        vertices = [vertex for neighbour in neighbours
                    for vertex in self.vertices
                    if np.all(vertex.vector == neighbour)]
        tile = Tile(self, tile_vector, vertices, index)
        return tile


    # Edges

    def initialise_edges(self):
        self.edges = []
        for tile in self.tiles:
            self.add_edges_around_tile(tile)

    def add_edges_around_tile(self, tile):
        vertex_offset = tile.vertices[1:] + [tile.vertices[0]]
        edges = [Edge(self, vertex_1, vertex_2)
                 for vertex_1, vertex_2 in zip(tile.vertices, vertex_offset)]
        new_edges = [edge for edge in edges if edge not in self.edges]
        self.edges = self.edges + new_edges


    # Saving

    def save_layout(self, name):
        path = self.get_layout_path(name)
        layout_json = self.get_layout_json()
        with open(path, "w+") as file:
            json.dump(layout_json, file, indent=2)

    def get_layout_path(self, name):
        self.layout_name = get_name(name)
        layout_path = self.get_path_layout()
        return layout_path

    def get_path_layout(self):
        file_name = f"{self.layout_name}.json"
        path = join(self.catan.path_layouts, file_name)
        return path

    def get_layout_json(self):
        layout_json = [
            {"Vector": self.json_iterable(tile.vector), "Type": tile.type,
             "Vertices": [vertex.ID for vertex in tile.vertices]}
            for tile in self.tiles]
        return layout_json

    def json_iterable(self, iterable):
        iterable = [int(i) for i in iterable]
        return iterable


    # Loading

    def load_layout(self, name):
        self.layout_name = name
        layout_json = self.load_layout_json()
        self.initialise_vertices()
        self.load_tiles(layout_json)
        self.initialise_edges()

    def load_layout_json(self):
        path = self.get_path_layout()
        with open(path, "r") as file:
            layout_json = json.load(file)
        return layout_json

    def load_tiles(self, layout_json):
        self.tiles = [
            Tile(self, np.array(tile_data["Vector"], dtype="int8"),
                 [self.vertices[index] for index in tile_data["Vertices"]],
                 index, tile_data["Type"])
            for index, tile_data in enumerate(layout_json)]


    # Produce layout

    def generate_layout(self, name=None):
        tile_types = self.get_generated_tile_types()
        self.set_layout(tile_types, name)

    def set_layout(self, tile_types, name=None):
        for tile, tile_type in zip(self.tiles, tile_types):
            tile.set_type(tile_type)
        self.save_layout(name)

    def get_generated_tile_types(self):
        tile_types = [tile_type for tile_type in self.tile_data
                      for index in range(self.tile_data[tile_type]["Count"])]
        shuffle(tile_types)
        return tile_types

    def input_layout(self, name=None):
        tile_types = self.get_input_tile_types()
        self.set_layout(tile_types, name)

    def get_input_tile_types(self):
        print(tile_type_prompt)
        tile_types = [self.get_tile_type_from_input()
                      for index in range(19)]
        return tile_types

    def get_tile_type_from_input(self):
        type_input = str(input())
        if type_input.lower() in tile_type_input_dict:
            return tile_type_input_dict[type_input.lower()].strip(" ")
        else:
            return "Desert"


    # Plotting

    def plot_board(self):
        self.initialise_plot()
        self.add_tiles_to_plot()
        self.set_x_and_y_plot_limits()

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
        vertex_positions = np.array(
            [vertex.position for vertex in self.vertices])
        min_x, min_y = np.min(vertex_positions, axis=0)*1.1
        max_x, max_y = np.max(vertex_positions, axis=0)*1.1
        self.ax.set_xlim(min_x, max_x)
        self.ax.set_ylim(min_y, max_y)

    def show(self):
        plt.show()

    def plot_state(self):
        self.plot_board()
        self.plot_settlements()
        self.plot_cities()
        self.plot_roads()

    def plot_settlements(self):
        for player in self.catan.players:
            self.plot_vertices(player.settlement_state,
                               player.colour, 5)

    def plot_cities(self):
        for player in self.catan.players:
            self.plot_vertices(player.city_state,
                               player.colour, 10)

    def plot_vertices(self, indicators, colour, size):
        for vertex, indicator in zip(self.vertices, indicators):
            if indicator:
                self.plot_vertex(vertex, colour, size)

    def plot_vertex(self, vertex, colour, size):
        pass

    def plot_roads(self):
        pass

    
    # Other

    def vertex_list(self, state_vertex):
        vertex_vectors = [
            vertex.vector for indicator, vertex in
            zip(state_vertex, self.vertices) if indicator]
        return vertex_vectors

    def edge_list(self, state_edge):
        edge_vectors = [
            (edge.vertex_1.vector, edge.vertex_2.vector)
            for indicator, vertex in zip(state_edge, self.edges)
            if indicator]
        return edge_vectors


tile_type_input_keys = {
    "Wheat ": ["1", "Wheat", "Crops", "W"],
    "Sheep ": ["2", "Sheep", "Wool", "S"],
    "Wood  ": ["3", "Wood", "Lumber",  "L"],
    "Ore   ": ["4", "Ore", "Stone", "Rock", "O", "S", "R"],
    "Mud   ": ["5", "Mud", "Clay", "Bricks", "M", "C", "B"],
    "Desert": ["6", "Desert", "D"]}

tile_type_keys_prompt = (
    '\n'.join(f"{key}   {', '.join(values)}"
              for key, values in tile_type_input_keys.items()))

tile_type_prompt = (
    "Enter the tile types going from left to right along the rows.\n"
    "Start at the top and work downwards.\n"
    "Use the following lookup:\n\n"
    f"{tile_type_keys_prompt}\n")

tile_type_input_dict = dict(
    (key.lower(), value)
    for value in tile_type_input_keys
    for key in tile_type_input_keys[value])













