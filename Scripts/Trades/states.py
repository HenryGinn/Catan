class States():

    def __init__(self, catan):
        self.catan = catan

    def initiate_state(self):
        self.state = {player.name: player.get_card_dict()
                      for player in self.catan.players}
