class Development():

    def get_trade_developments(self, player_name, state):
        name = f"{player_name} view {player_name}"
        development_trades = [
            self.get_development_trades_type(development_type, name, state)
            for development_type in self.catan.developments()]
        return development_trades

    def get_playable_developments_type(self, development_type, name, state):
        if state[name][development_type] > 0:
            return self.do_get_playable_development_types(
                development_type, name, state)

    def do_get_playable_development_types(self, development_type, *args):
        match development_type:
            case "Harvest"    : return self.get_playable_harvest(*args)
            case "Knight"     : return self.get_playable_knight(*args)
            case "RoadBuilder": return self.get_playable_road_builder(*args)
            case "Monopoly"   : return self.get_playable_monopoly(*args)








