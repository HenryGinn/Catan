class Turn():

    trade_limit = 10
    
    def __init__(self, catan):
        self.catan = catan
        self.set_player()
        self.trade_count = 0
        self.played_development_card = False

    def set_player(self):
        self.catan.moves += 1
        turn = self.catan.moves % 4
        self.player = self.catan.players[turn]

    def take_turn(self):
        while self.trade_count < self.trade_limit:
            self.trade_with_players()
            self.trade_assets()
            self.trade_play_development_card()

    def trade_with_players(self):
        pass

    def trade_assets(self):
        pass

    def trade_play_development_card(self):
        if not self.played_development_card:
            self.do_trade_play_development_card()

    def do_trade_play_development_card(self):
        pass


    # Manually trading.
    # Converting a human-readable input into the machine-readable
    # description and then executing it.

    def trade_players_input(self, trade):
        pass

    def trade_assets_input(self, trade):
        pass

    def play_development_input(self, trade):
        pass
