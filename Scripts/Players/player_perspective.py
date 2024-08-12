from Players.player import Player


class PlayerPerspective(Player):

    player_type = "Perspective"

    def __init__(self, ID, player_base):
        super().__init__(player_base.catan, ID)
        self.player_base = player_base
        self.name = f"{self.player_base.name} view {self.ID + 1}"

    def initialise_card_state(self):
        resource_card_state = self.get_initial_resources()
        development_card_state = self.get_initial_developments()
        self.card_state = {
            **resource_card_state, **development_card_state}

    def get_initial_resources(self):
        resource_card_state = {f"{resource} {bound}": 0
                               for resource in resource_types
                               for bound in ["Min", "Max"]}
        return resource_card_state

    def get_initial_developments(self):
        development_card_state = {f"{development} {bound}": 0
                                  for development in development_types
                                  for bound in ["Min", "Max"]}
        return development_card_state


resource_types = ["Wheat", "Sheep", "Wood", "Ore", "Mud"]
development_types = ["Knight", "Victory", "Monopoly", "RoadBuilder", "Harvest"]
