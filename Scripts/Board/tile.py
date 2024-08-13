import numpy as np


class Tile():

    def __init__(self, board, tile_data):
        self.board = board
        self.vector = np.array(tile_data["Vector"]).astype("int8")
        self.vertices = [board.vertices[index]
                         for index in tile_data["Vertices"]]
        self.set_type("Desert")

    def set_type(self, tile_type):
        self.type = tile_type
        self.color = self.board.tile_data[tile_type]["Color"]

