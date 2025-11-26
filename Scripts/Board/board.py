import os

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Annulus
from matplotlib.collections import PatchCollection
from hgutilities.utils import json

from Board.vertex import Vertex
from Board.tile import Tile
from Board.port import Port
from Board.edge import Edge
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
        for tile in self.tiles:
            self.add_edges_around_tile(tile)
        self.edges = np.array(self.edges)

    def add_edges_around_tile(self, tile):
        vertex_offset = tile.vertices[1:] + [tile.vertices[0]]
        edges_around_tile = self.get_edges_around_tile(tile, vertex_offset)
        new_edges = [edge for edge in edges_around_tile if edge not in self.edges]
        self.edges = self.edges + new_edges

    def get_edges_around_tile(self, tile, vertex_offset):
        edges_around_tile = [
            Edge(self, vertex_1, vertex_2)
            for vertex_1, vertex_2 in zip(tile.vertices, vertex_offset)
            if vertex_1.ID < vertex_2.ID]
        return edges_around_tile


    # Saving

    def save_layout(self, name=None):
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
        tile_types = self.get_input_tile_types()
        self.set_tile_types(tile_types)

    def get_input_tile_types(self):
        print(tile_type_prompt)
        tile_types = [
            self.get_tile_type_from_input()
            for index in range(19)]
        return tile_types

    def get_tile_type_from_input(self):
        type_input = str(input())
        if type_input.lower() in tile_type_input_dict:
            return tile_type_input_dict[type_input.lower()].strip(" ")
        else:
            return "Desert"


    # Lookups

    def set_lookups(self):
        self.set_vertex_index_lookup_from_tile_and_vertex()
        self.set_edge_index_lookup_from_tile_and_edge()

    def set_vertex_index_lookup_from_tile_and_vertex(self):
        self.vertex_index_lookup_from_tile_and_vertex = {
            (tile_index, vertex_index): self.vertices.index(vertex)
            for tile_index, tile in enumerate(self.tiles)
            for vertex_index, vertex in enumerate(self.tiles.vertices)}

    def set_edge_index_lookup_from_tile_and_edge(self):
        self.edge_index_lookup_from_tile_and_edge = {
            (tile_index, vertex_index): self.vertices.index(vertex)
            for tile_index, tile in enumerate(self.tiles)
            for edge_index, edge in enumerate(self.tiles.edges)}


    # Plotting

    def show_layout(self):
        self.initialise_plot_show()
        self.plot_layout()
        plt.show()

    def save_layout_plot(self):
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
        self.add_robber()
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
                ha="center", va="center", fontsize=20)

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
                ha='center', va='center', fontsize=20))

    def add_robber(self):
        robber_tile = self.tiles[self.game.robber_index]
        annulus = Annulus(robber_tile.position, 0.7, 0.15, color="black")
        self.ax.add_patch(annulus)

    def set_x_and_y_plot_limits(self):
        positions = np.array(
            [obj.position for obj in self.vertices + self.ports])
        min_x, min_y = np.min(positions, axis=0)*1.15
        max_x, max_y = np.max(positions, axis=0)*1.15
        self.ax.set_xlim(min_x, max_x)
        self.ax.set_ylim(min_y, max_y)

    def show_state(self):
        self.initialise_plot_show()
        self.plot_state()
        plt.show()

    def save_state(self):
        self.initialise_plot_save()
        self.plot_state()
        path = os.path.join(
            self.game.path, f"BoardState_{self.game.move:04}.pdf")
        plt.savefig(path)
        self.log.info(f"Saved board state to {path}")

    def plot_state(self):
        self.plot_layout()
        self.plot_settlements()
        self.plot_cities()
        self.plot_roads()

    def plot_settlements(self):
        for player in self.game.players:
            self.plot_vertices(
                player.geometry_state["Settlements"],
                player.color, 0.15)

    def plot_cities(self):
        for player in self.game.players:
            self.plot_vertices(
                player.geometry_state["Cities"],
                player.color, 0.25)

    def plot_vertices(self, indicators, color, size):
        for vertex, indicator in zip(self.vertices, indicators):
            if indicator:
                self.plot_vertex(vertex, color, size)

    def plot_vertex(self, vertex, color, size):
        circle = plt.Circle(vertex.position, size, color=color)
        self.ax.add_patch(circle)

    def plot_roads(self):
        for player in self.game.players:
            self.plot_edges(
                player.geometry_state["Roads"],
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
        self.ax.plot(*values, color=color, linewidth=6)


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
    
    def get_tile_input(self):
        tile_number = int(input(tile_number_prompt))
        if tile_number == 7:
            return self.get_tile_number_desert()
        else:
            return self.get_tile_number_non_desert()

    def get_tile_number_desert(self):
        tile_index = [
            index for index, tile in enumerate(self.tiles)
            if tile.number is None]
        return tile_index

    def get_tile_number_non_desert(self):
        tile_order = int(input(tile_order_prompt)) - 1
        tile_index = [
            index for index, tile in enumerate(self.tiles)
            if tile.number == tile_number][tile_order]
        return tile_index

    def get_vertex_input(self):
        print("Pick a tile that the edge borders")
        tile_index = self.get_tile_input()
        tile = self.tiles[tile_index]
        vertex_index = int(input(vertex_input_prompt))
        vertex_index = [
            index for index, vertex in enumerate(self.vertices)
            if tile.vertices[vertex_index] is vertex][0]
        return vertex_index

    def get_edge_input(self):
        print("Pick a tile the edge borders")
        tile_index = self.get_tile_input()
        edge_index = int(input(edge_input_prompt))
    

tile_type_input_keys = {
    "Wheat ": ["1", "Wheat", "Crops", "W"],
    "Sheep ": ["2", "Sheep", "Wool", "S"],
    "Wood  ": ["3", "Wood", "Lumber",  "L"],
    "Ore   ": ["4", "Ore", "Stone", "Rock", "O", "S", "R"],
    "Mud   ": ["5", "Mud", "Clay", "Bricks", "M", "C", "B"],
    "Desert": ["6", "Desert", "D"]}

tile_type_keys_prompt = (
    '\n'.join(
        f"{key}   {', '.join(values)}"
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

tile_number_prompt = (
    "What is the number on the tile?\n"
    "Use 7 for a desert")
tile_order_prompt = "Does this tile number appear first or second (1 or 2?):\n"
vertex_input_prompt = (
    "Starting with the top of the hexagon as 1,\n"
    "what number is the vertex:\n")
edge_input_prompt = (
    "Starting with the top right edge of the hexagon as 1,\n"
    "what number is the edge:\n")
