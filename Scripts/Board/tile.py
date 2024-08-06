class Tile():

    def __init__(self, board, vector, vertices, ID, tile_type="Desert"):
        self.board = board
        self.vector = vector
        self.vertices = vertices
        self.ID = ID
        self.set_type(tile_type)

    def set_type(self, tile_type):
        self.type = tile_type
        self.color = self.board.tile_data[tile_type]["Color"]

