from Board.tile import Tile


class Port(Tile):

    def __init__(self, board, port_data):
        super().__init__(board, port_data)
        self.type = port_data["Type"]
        self.ratio = port_data["Ratio"]
