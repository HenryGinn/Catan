from hgutilities.utils import get_dict_string


class Player():

    def __init__(self, game, name):
        self.game = game
        self.name = name
        self.log = self.game.log
