import os

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Annulus
from matplotlib.collections import PatchCollection
from hgutilities.utils import json

from Board.vertex import Vertex
from Board.tile import Tile
from Board.port import Port
from utils import get_name
from global_variables import (
    path_resources,
    path_layouts,
    tile_numbers,
    tile_types_list)


class Board():

    basis = np.array([[0, 1], [np.sin(np.pi/3), np.cos(np.pi/3)]])
    directions = np.array([
        [1, 0], [0, 1], [-1, 1],
        [-1, 0], [0, -1], [1, -1]])

    def __init__(self, game):
        self.game = game
        self.log = game.log
        np.random.seed(game.seed)
        self.load_tile_definitions()
        self.initialise_graph_components()

    def load_tile_definitions(self):
        path = os.path.join(path_resources, "Tile Definitions.json")
        with open(path, "r") as file:
            self.tile_definitions = json.load(file)

    def initialise_graph_components(self):
        self.initialise_vertices()
        self.initialise_tiles()
        self.initialise_ports()
        self.initialise_edges()


    # Vertices

    def initialise_vertices(self):
        vertex_vectors = self.get_vertex_position_vectors()
        self.vertices = [
            Vertex(self, position_vector, index)
            for index, position_vector in
            enumerate(vertex_vectors)]

    def get_vertex_position_vectors(self):
        path = os.path.join(path_resources, "Vertex Positions.json")
        with open(path, "r") as file:
            vertex_vectors = [tuple(vector) for vector in json.load(file)]
        return vertex_vectors


    # Tiles

    def initialise_tiles(self):
        tiles_data = self.load_tiles_data()
        self.tiles = [
            Tile(self, tile_definitions)
            for tile_definitions in tiles_data]        

    def load_tiles_data(self):
        path = os.path.join(path_resources, "Tiles Data.json")
        with open(path, "r") as file:
            tiles_data = json.load(file)
        return tiles_data

    def initialise_ports(self):
        ports_data = self.get_ports_data()
        self.ports = [
            Port(self, port_data)
            for port_data in ports_data]

    def get_ports_data(self):
        path = os.path.join(path_resources, "Ports Data.json")
        with open(path, "r") as file:
            ports_data = json.load(file)
        return ports_data

    def set_tile_states(self):
        self.tile_states = {
            tile_type: np.array([
                tile.type == tile_type
                for tile in self.tiles]).astype("int8")
            for tile_type in tile_types_list}


    # Edges

    def initialise_edges(self):
        self.edges = []
        self.add_edges_around_tiles()
        self.edges = np.array(self.edges)
        self.extract_unique_edges()

    def add_edges_around_tiles(self):
        for tile in self.tiles:
            edges_around_tile = tile.get_init_edges_around_tile()
            self.edges = self.edges + edges_around_tile

    def extract_unique_edges(self):
        midpoints = np.array([
            edge.get_midpoint() for edge in self.edges])
        _, indexes = np.unique(midpoints, axis=0, return_index=True)
        self.edges = self.edges[indexes]


    # Saving

    def save_layout(self, name=None):
        if name is not None:
            self.save_layout_with_name(name)
        else:
            self.log.info("Layout not saved as no name was given")

    def save_layout_with_name(self, name):
        path = self.get_path_tile_data(name)
        tile_data = self.get_tile_data()
        with open(path, "w+") as file:
            json.dump(tile_data, file, indent=2)
        self.log.info(f"Saving layout to {path}")

    def get_tile_data(self):
        tile_data = [
            {"Type": tile.type,
             "Number": tile.number}
            for tile in self.tiles]
        return tile_data

    def get_path_tile_data(self, name=None):
        self.set_layout_name(name)
        file_name = f"{self.layout_name}.json"
        path = os.path.join(path_layouts, file_name)
        return path

    def set_layout_name(self, name):
        if (not hasattr(self, "layout_name")
            or self.layout_name is None):
            self.layout_name = get_name(name)


    # Loading

    def load_layout(self, name):
        self.log.info(f"Loading layout {name}")
        self.layout_name = name
        tile_data = self.load_tile_data()
        self.set_tile_data(tile_data)
        self.set_lookups()

    def load_tile_data(self):
        path = self.get_path_tile_data()
        with open(path, "r") as file:
            tile_data = json.load(file)
        return tile_data

    def set_tile_data(self, tile_data):
        for tile, data in zip(self.tiles, tile_data):
            tile.set_type(data["Type"])
            tile.number = data["Number"]
        self.set_tile_states()


    # Produce layout

    def generate_layout(self, name=None):
        self.log.info("Generating layout")
        self.set_generate_tile_types()
        self.set_generate_tile_numbers()
        self.save_layout(name)
        self.set_lookups()

    def set_generate_tile_types(self):
        tile_types = self.get_generated_tile_types()
        for tile, tile_type in zip(self.tiles, tile_types):
            tile.set_type(tile_type)

    def get_generated_tile_types(self):
        tile_types = [
            tile_type
            for tile_type, definition in self.tile_definitions.items()
            for index in range(definition["Count"])]
        np.random.shuffle(tile_types)
        return tile_types

    def set_generate_tile_numbers(self):
        np.random.shuffle(tile_numbers)
        index = 0
        for tile in self.tiles:
            if tile.type != "Desert":
                tile.number = tile_numbers[index]
                index += 1
            else:
                tile.number = None

    def input_layout(self, name=None):
        self.set_tile_types_from_input()
        self.set_tile_numbers_from_input()
        self.save_layout(name)

    def set_tile_types_from_input(self):
        print(tile_types_prompt)
        for tile in self.tiles:
            tile.set_type(self.get_tile_type_from_input())

    def get_tile_type_from_input(self):
        invalid_input = True
        while invalid_input:
            type_input = str(input())
            if type_input.lower() not in tile_type_input_dict:
                print("Invalid input, try again")
            else:
                invalid_input = False
        return tile_type_input_dict[type_input.lower()]

    def set_tile_numbers_from_input(self):
        print(tile_numbers_prompt)
        self.tile_number_input_is_invalid = True
        while self.tile_number_input_is_invalid:
            for tile in self.tiles:
                self.set_tile_number_from_input(tile)
            self.ensure_valid_tile_numbers_from_input()

    def set_tile_number_from_input(self, tile):
        if tile.type != "Desert":
            tile.number = self.get_tile_number_from_input(tile)
        else:
            tile.number = None

    def get_tile_number_from_input(self, tile):
        prompt = f"{tile.type}:".ljust(7)
        tile_number = int(input(prompt))
        return tile_number

    def ensure_valid_tile_numbers_from_input(self):
        input_tile_numbers = sorted([
            tile.number for tile in self.tiles
            if tile.number is not None])
        if input_tile_numbers != sorted(tile_numbers):
            print(f"Incorrect tile numbers:\n{input_tile_numbers}\n")
        else:
            self.tile_number_input_is_invalid = False
    

    # Lookups

    def set_lookups(self):
        self.set_vertex_index_lookup_from_tile_and_vertex()
        self.set_edge_index_lookup_from_tile_and_edge()

    def set_vertex_index_lookup_from_tile_and_vertex(self):
        self.vertex_index_lookup_from_tile_and_vertex = {
            (tile_index, vertex_index): self.vertices.index(vertex)
            for tile_index, tile in enumerate(self.tiles)
            for vertex_index, vertex in enumerate(tile.vertices)}

    def set_edge_index_lookup_from_tile_and_edge(self):
        self.edge_index_lookup_from_tile_and_edge = {
            (tile_index, edge_index): np.where(self.edges == edge)[0][0]
            for tile_index, tile in enumerate(self.tiles)
            for edge_index, edge in enumerate(
                tile.get_edges_around_tile())}


    # Plotting

    def show_tiles(self):
        self.initialise_plot_show()
        self.plot_layout()
        plt.show()

    def save_tiles(self):
        self.initialise_plot_save()
        self.plot_layout()
        path = os.path.join(
            self.game.path, "Layout.pdf")
        plt.savefig(path)
        self.log.info(f"Saved board layout to {path}")
    
    def plot_layout(self):
        self.add_tiles_to_plot()
        self.add_numbers_to_plot()
        self.add_ports_to_plot()
        self.set_x_and_y_plot_limits()

    def initialise_plot_show(self):
        self.fig = plt.figure(figsize=(12, 8))
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_aspect("equal")
        self.ax.axis("off")
        self.fig.patch.set_facecolor("#002240")

    def initialise_plot_save(self):
        self.fig = plt.figure(figsize=(8, 8))
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_aspect("equal")
        self.ax.axis("off")

    def add_tiles_to_plot(self):
        polygons = PatchCollection(
            [Polygon([vertex.position for vertex in tile.vertices],
                     closed=True, facecolor=tile.color, edgecolor="k")
             for tile in self.tiles], match_original=True)
        self.ax.add_collection(polygons)

    def add_numbers_to_plot(self):
        for tile in self.tiles:
            self.ax.text(
                *tile.position, tile.number,
                ha="center", va="center", fontsize=30)

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
            self.ax.add_artist(plt.Text(
                *port.position, str(port.ratio),
                ha='center', va='center', fontsize=30))

    def plot_robber(self):
        robber_tile = self.tiles[self.game.robber_index]
        annulus = Annulus(robber_tile.position, 0.5, 0.1, color="black")
        self.ax.add_patch(annulus)

    def set_x_and_y_plot_limits(self):
        positions = np.array(
            [obj.position for obj in self.vertices + self.ports])
        min_x, min_y = np.min(positions, axis=0)*1.15
        max_x, max_y = np.max(positions, axis=0)*1.15
        self.ax.set_xlim(min_x, max_x)
        self.ax.set_ylim(min_y, max_y)

    def show_board(self):
        self.initialise_plot_show()
        self.plot_board()
        plt.show()

    def save_board(self):
        self.initialise_plot_save()
        self.plot_board()
        path = os.path.join(
            self.game.path, f"BoardState_{self.game.move:04}.pdf")
        plt.savefig(path)
        self.log.info(f"Saved board state to {path}")

    def plot_board(self):
        self.plot_layout()
        self.plot_roads()
        self.plot_settlements()
        self.plot_cities()
        self.plot_robber()

    def plot_settlements(self):
        for player in self.game.players:
            self.plot_vertices(
                player.real_estate["Settlements"],
                player.color, 0.2)

    def plot_cities(self):
        for player in self.game.players:
            self.plot_vertices(
                player.real_estate["Cities"],
                player.color, 0.3)

    def plot_vertices(self, indicators, color, size):
        for vertex, indicator in zip(self.vertices, indicators):
            if indicator:
                self.plot_vertex(vertex, color, size)

    def plot_vertex(self, vertex, color, size):
        circle = plt.Circle(vertex.position, size, color=color, zorder=1.2)
        self.ax.add_patch(circle)

    def plot_roads(self):
        for player in self.game.players:
            self.plot_edges(
                player.real_estate["Roads"],
                player.color)

    def plot_edges(self, indicators, color):
        for edge, indicator in zip(self.edges, indicators):
            if indicator:
                self.plot_edge(edge, color)

    def plot_edge(self, edge, color):
        values = [[
            vertex.position[i]
            for vertex in edge.vertices]
                  for i in range(2)]
        self.ax.plot(*values, color=color, linewidth=9, zorder=1.1)


    # Other

    def get_string(self, state, structure_type):
        match structure_type:
            case "Vertex": return self.get_vertex_string(state)
            case "Edge"  : return self.get_edge_string(state)

    def get_vertex_string(self, state_vertex):
        vertex_vectors = self.get_vertex_vectors(state_vertex)
        string = ", ".join(
            f"({vector[0]}, {vector[1]})"
            for vector in vertex_vectors)
        return string

    def get_vertex_vectors(self, state_vertex):
        vertex_vectors = [
            vertex.vector for indicator, vertex in
            zip(state_vertex, self.vertices) if indicator]
        return vertex_vectors

    def get_edge_string(self, state_edge):
        edge_vector_pairs = self.get_edge_vector_pairs(state_edge)
        string = ", ".join(
            f"(({pair[0][0]}, {pair[0][1]}),"
            f"({pair[1][0]}, {pair[1][1]}))"
            for pair in edge_vector_pairs)
        return string

    def get_edge_vector_pairs(self, state_edge):
        edge_vectors = [
            tuple([vertex.vector for vertex in edge.vertices])
            for indicator, edge in zip(state_edge, self.edges)
            if indicator]
        return edge_vectors

    def get_state(self, vectors, real_estate):
        match self.game.real_estate[real_estate]:
            case "Vertex": return self.get_vertex_state(vectors)
            case "Edge"  : return self.get_edge_state(vectors)

    def get_vertex_state(self, vectors):
        vertex_state = np.array(
            [vertex.vector in vectors
             for vertex in self.vertices])
        return vertex_state

    def get_edge_state(self, edges):
        edge_state = np.array([
            edge.get_vectors() in edges
            for edge in self.edges])
        return edge_state

    def get_position(self, vector):
        position = np.dot(np.array(vector), self.basis)
        return position


    # Input for interacting with the board
    
    def get_tile_indexes(self):
        tile_number = self.get_tile_number_input()
        tile_order = self.get_tile_order_input(tile_number)
        return tile_number, tile_order

    def get_tile_number_input(self):
        tile_number = int(input(tile_number_prompt))
        if tile_number == 7:
            tile_number = None
        return tile_number

    def get_tile_order_input(self, tile_number):
        tile_order = 0
        if tile_number != 7:
            tile_order = int(input(tile_order_prompt)) - 1
        return tile_order

    def get_tile_index_from_indexes(self, tile_number, tile_order):
        tile_index = [
            index for index, tile in enumerate(self.tiles)
            if tile.number == tile_number][tile_order]
        return tile_index

    def get_vertex_indexes(self):
        print("Pick a tile that the vertex borders")
        tile_number, tile_order = self.get_tile_indexes()
        neighbour_index = int(input(vertex_input_prompt)) - 1
        return tile_number, tile_order, neighbour_index

    def get_vertex_index_from_indexes(self, tile_number, tile_order, neighbour_index):
        tile_index = self.get_tile_index_from_indexes(tile_number, tile_order)
        tile = self.tiles[tile_index]
        vertex_index = self.vertex_index_lookup_from_tile_and_vertex[
            (tile_index, neighbour_index)]
        return vertex_index

    def get_edge_indexes(self):
        print("Pick a tile that the edge borders")
        tile_number, tile_order = self.get_tile_indexes()
        neighbour_index = int(input(edge_input_prompt)) - 1
        return tile_number, tile_order, neighbour_index

    def get_edge_index_from_indexes(self, tile_number, tile_order, neighbour_index):
        tile_index = self.get_tile_index_from_indexes(tile_number, tile_order)
        tile = self.tiles[tile_index]
        edge_index = self.edge_index_lookup_from_tile_and_edge[
            (tile_index, neighbour_index)]
        return edge_index
    

tile_type_input_keys = {
    "Wheat" : ["1", "Wheat", "Crops", "W"],
    "Sheep" : ["2", "Sheep", "Wool", "S"],
    "Wood"  : ["3", "Wood", "Lumber",  "L"],
    "Ore"   : ["4", "Ore", "Stone", "Rock", "O", "R"],
    "Mud"   : ["5", "Mud", "Clay", "Bricks", "M", "C", "B"],
    "Desert": ["6", "Desert", "D"]}

tile_type_keys_prompt = (
    '\n'.join(
        f"{key.ljust(6)}   {', '.join(values)}"
        for key, values in tile_type_input_keys.items()))

tile_types_prompt = (
    "Enter the tile types going from left to right along the rows.\n"
    "Start at the top and work downwards.\n"
    "Use the following lookup:\n\n"
    f"{tile_type_keys_prompt}\n")

tile_numbers_prompt = (
    "Enter the tile number in the same order as the tile types were input.\n"
    "The desert tile will be skipped")

tile_type_input_dict = dict(
    (key.lower(), value)
    for value in tile_type_input_keys
    for key in tile_type_input_keys[value])

tile_number_prompt = (
    "What is the number on the tile?\n"
    "Use 7 for a desert\n")

tile_order_prompt = "Does this tile number appear first or second (1 or 2?):\n"

vertex_input_prompt = (
    "Starting with the top of the hexagon as 1,\n"
    "what number is the vertex:\n")

edge_input_prompt = (
    "Starting with the top right edge of the hexagon as 1,\n"
    "what number is the edge:\n")
