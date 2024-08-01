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

    basis = np.array([[0, 1], [np.sin(np.pi/3), np.cos(np.pi/3)]])

    def __init__(self, vector):
        self.vector = vector

    def set_position(self):
        self.position = np.dot(self.vector, self.basis)
