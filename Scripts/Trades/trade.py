"""
What a player has and thinks all other players have is
called a player state. The game state is the collection
of all the player states. The neural network evaluates
player states.

A state is a list. This is to match with the fact that
the neural network evaluates states. The game state is
a list of these lists.

This class takes in the game state and a possible trade
and returns the updated game state.
"""


class Trade():

    def __init__(self, catan):
        self.catan = catan
