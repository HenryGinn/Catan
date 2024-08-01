class Tile():

    def __init__(self, board, vector, vertices):
        self.board = board
        self.vector = vector
        self.vertices = vertices
        self.set_type("Desert")

    def set_type(self, tile_type):
        self.type = tile_type
        self.color = self.board.tile_data[tile_type]["Color"]

