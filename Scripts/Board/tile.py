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
        self.vertices = [
            self.board.vertices[index]
            for index in vertex_data]

    def set_type(self, tile_type):
        self.type = tile_type
        self.color = self.board.tile_definitions[tile_type]["Color"]

