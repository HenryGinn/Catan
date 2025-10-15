from Players.player import Player
from global_variables import initial_state


class PlayerPerspective(Player):

    def __init__(self, perspective, base):
        name = f"{base.name} view {perspective.name}"
        self.view = f"{perspective.name}"
        super().__init__(base.catan, name)
        self.base = base
        self.them = perspective
        self.card_state = initial_state.copy()

    def __str__(self):
        df = self.catan.get_perspective_df(self.name, self.card_state)
        string = df.to_string()
        return string
