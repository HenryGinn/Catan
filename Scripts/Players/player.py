"""
The following is the definition of state for a player view.
The definition of state for a regular player is the
concantenation of the state for a view of each player.

wheat_min, wheat_max,
sheep_min, sheep_max,
wood_min, wood_max,
ore_min, ore_max,
mud_min, mud_max,

victory_min, victory_max,
monopoly_min, monopoly_max,
knight_min, knight_max, knights_played,
harvest_min, harvest_max,
road_min, road_max,

(lists of booleans)
settlement vertices
city vertices
road edges
robber vertices
"""


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
