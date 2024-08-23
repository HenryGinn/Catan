from hgutilities.utils import get_dict_string


class Player():

    player_type = "General"
    
    def __init__(self, catan, name):
        self.catan = catan
        self.name = name

    def __str__(self):
        state_dict = self.get_state_dict()
        string = get_dict_string(state_dict)
        return string
