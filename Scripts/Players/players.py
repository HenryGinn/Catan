from Players.player import Player
from Players.player_regular import PlayerRegular


class Players():

    def __init__(self, catan):
        self.catan = catan
        self.initialise_players()

    def initialise_players(self):
        self.players = [PlayerRegular(self, index)
                        for index in range(4)]
