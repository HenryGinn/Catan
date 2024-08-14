from Board.tile import Tile


class Port(Tile):

    def __init__(self, board, port_data):
        super().__init__(board, port_data)
        self.ratio = port_data["Ratio"]
        self.set_type(port_data["Type"])
