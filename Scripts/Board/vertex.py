"""
There are three different coordinate systems used here.

vertex: this is the position with respect to a basis adapted to
    a hexagon. This is given by the attribute, 'basis'.
    
position: this is the position in Cartesian coordinates. This
    is used for graphical representations of the board.

polar: this is not used explicitely, but will be evident in
    the structure of neural network.
"""


import numpy as np


class Vertex():

    def __init__(self, board, vector, ID):
        self.board = board
        self.vector = vector
        self.ID = ID
        self.position = self.board.get_position(self.vector)
