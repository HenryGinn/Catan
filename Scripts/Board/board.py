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
from Board.port import Port
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
        self.initialise_ports()
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
            vertex_vectors = [tuple(vector) for vector in load(file)]
        return vertex_vectors


    # Tiles

    def initialise_tiles(self):
        tiles_data = self.load_tiles_data()
        self.tiles = [Tile(self, tile_data)
                      for tile_data in tiles_data]

    def load_tiles_data(self):
        path = join(self.catan.path_resources, "Tiles Data.json")
        with open(path, "r") as file:
            tiles_data = load(file)
        return tiles_data

    def initialise_ports(self):
        ports_data = self.get_ports_date()
        self.ports = [Port(self, port_data)
                      for port_data in ports_data]

    def get_ports_date(self):
        path = join(self.catan.path_resources, "Ports Data.json")
        with open(path, "r") as file:
            ports_data = json.load(file)
        return ports_data


    # Edges

    def initialise_edges(self):
        self.edges = []
        for tile in self.tiles:
            self.add_edges_around_tile(tile)

    def add_edges_around_tile(self, tile):
        vertex_offset = tile.vertices[1:] + [tile.vertices[0]]
        edges = [Edge(self, vertex_1, vertex_2)
                 for vertex_1, vertex_2 in zip(tile.vertices, vertex_offset)
                 if vertex_1.ID < vertex_2.ID]
        new_edges = [edge for edge in edges if edge not in self.edges]
        self.edges = self.edges + new_edges


    # Saving

    def save_layout(self, name=None):
        path = self.get_path_tile_types(name)
        tile_types = [tile.type for tile in self.tiles]
        with open(path, "w+") as file:
            json.dump(tile_types, file, indent=2)

    def get_path_tile_types(self, name=None):
        self.set_layout_name(name)
        file_name = f"{self.layout_name}.json"
        path = join(self.catan.path_layouts, file_name)
        return path

    def set_layout_name(self, name):
        if (not hasattr(self, "layout_name")
            or self.layout_name is None):
            self.layout_name = get_name(name)

    def json_iterable(self, iterable):
        iterable = [int(i) for i in iterable]
        return iterable


    # Loading

    def load_layout(self, name):
        self.layout_name = name
        tile_types = self.load_tile_types()
        self.set_tile_types(tile_types)

    def load_tile_types(self):
        path = self.get_path_tile_types()
        with open(path, "r") as file:
            tile_types = json.load(file)
        return tile_types

    def set_tile_types(self, tile_types):
        for tile, tile_type in zip(self.tiles, tile_types):
            tile.set_type(tile_type)


    # Produce layout

    def generate_layout(self, name=None):
        tile_types = self.get_generated_tile_types()
        self.set_tile_types(tile_types)
        self.save_layout(name)

    def set_layout(self, tile_types, name=None):
        for tile, tile_type in zip(self.tiles, tile_types):
            tile.set_type(tile_type)

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

    def plot_layout(self):
        self.initialise_plot()
        self.add_tiles_to_plot()
        self.add_ports_to_plot()
        self.set_x_and_y_plot_limits()

    def initialise_plot(self):
        self.fig, self.ax = plt.subplots(1, figsize=(12, 8))
        self.ax.set_aspect("equal")
        self.ax.axis("off")
        self.fig.patch.set_facecolor("#002240")

    def add_tiles_to_plot(self):
        polygons = PatchCollection(
            [Polygon([vertex.position for vertex in tile.vertices],
                     closed=True, facecolor=tile.color, edgecolor="k")
             for tile in self.tiles], match_original=True)
        self.ax.add_collection(polygons)

    def add_ports_to_plot(self):
        self.add_port_piers_to_plot()
        self.add_port_circles_to_plot()
        self.add_port_text_to_plot()

    def add_port_piers_to_plot(self):
        for port in self.ports:
            for vertex in port.vertices:
                values = list(zip(*[vertex.position, port.position]))
                self.ax.plot(*values, color=port.color, linewidth=6, zorder=-1)

    def add_port_circles_to_plot(self):
        circles = PatchCollection(
            [plt.Circle(port.position, 0.5, color=port.color)
             for port in self.ports], match_original=True)
        self.ax.add_collection(circles)

    def add_port_text_to_plot(self):
        for port in self.ports:
            self.ax.add_artist(
                plt.Text(*port.position, str(port.ratio),
                         ha='center', va='center', fontsize=20))

    def set_x_and_y_plot_limits(self):
        positions = np.array(
            [obj.position for obj in self.vertices + self.ports])
        min_x, min_y = np.min(positions, axis=0)*1.15
        max_x, max_y = np.max(positions, axis=0)*1.15
        self.ax.set_xlim(min_x, max_x)
        self.ax.set_ylim(min_y, max_y)

    def show(self):
        plt.show()

    def plot_state(self):
        self.plot_layout()
        self.plot_settlements()
        self.plot_cities()
        self.plot_roads()
        self.show()

    def plot_settlements(self):
        for player in self.catan.players:
            self.plot_vertices(player.settlement_state,
                               player.color, 0.15)

    def plot_cities(self):
        for player in self.catan.players:
            self.plot_vertices(player.city_state,
                               player.color, 0.25)

    def plot_vertices(self, indicators, color, size):
        for vertex, indicator in zip(self.vertices, indicators):
            if indicator:
                self.plot_vertex(vertex, color, size)

    def plot_vertex(self, vertex, color, size):
        circle = plt.Circle(vertex.position, size, color=color)
        self.ax.add_patch(circle)

    def plot_roads(self):
        for player in self.catan.players:
            self.plot_edges(player.road_state,
                            player.color)

    def plot_edges(self, indicators, color):
        for edge, indicator in zip(self.edges, indicators):
            if indicator:
                self.plot_edge(edge, color)

    def plot_edge(self, edge, color):
        values = [[vertex.position[i]
                   for vertex in edge.vertices]
                  for i in range(2)]
        self.ax.plot(*values, color=color, linewidth=6)


    # Other

    def get_vertex_string(self, state_vertex):
        vertex_vectors = self.get_vertex_vectors(state_vertex)
        string = ", ".join(f"({vector[0]}, {vector[1]})"
                           for vector in vertex_vectors)
        return string

    def get_vertex_vectors(self, state_vertex):
        vertex_vectors = [
            vertex.vector for indicator, vertex in
            zip(state_vertex, self.vertices) if indicator]
        return vertex_vectors

    def get_edge_string(self, state_edge):
        edge_vector_pairs = self.get_edge_vector_pairs(state_edge)
        string = ", ".join(f"(({pair[0][0]}, {pair[0][1]}),"
                            f"({pair[1][0]}, {pair[1][1]}))"
                           for pair in edge_vector_pairs)
        return string

    def get_edge_vector_pairs(self, state_edge):
        edge_vectors = [
            tuple([vertex.vector for vertex in edge.vertices])
            for indicator, edge in zip(state_edge, self.edges)
            if indicator]
        return edge_vectors

    def get_vertex_state(self, vectors):
        vertex_state = np.array(
            [vertex.vector in vectors
             for vertex in self.vertices])
        return vertex_state

    def get_edge_state(self, edges):
        edge_state = np.array(
            [edge.get_vectors() in edges
             for edge in self.edges])
        return edge_state

    def get_position(self, vector):
        position = np.dot(np.array(vector), self.basis)
        return position


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













