import time
import json
from os.path import join
from random import shuffle


class LayoutSetup():

    def __init__(self, catan):
        self.catan = catan

    def generate_layout(self, name=None):
        self.set_layout_path(name)
        self.load_tile_definitions()
        self.randomize_layout()

    def set_layout_path(self, name):
        self.set_layout_name(name)
        self.path_layout = join(
            self.catan.path_layouts, self.layout_name)

    def set_layout_name(self, name):
        if name is None:
            self.layout_name = time.strftime("%Y_%M_%d__%H_%M")
        else:
            self.layout_name = name

    def load_tile_definitions(self):
        path = join(self.catan.path_resources, "Tile Definitions.json")
        with open(path, "r") as file:
            self.tile_definitions = json.load(file)

    def randomize_layout(self):
        tiles = [key for key, value in self.tile_definitions.items()
                 for i in range(value)]
        tiles = shuffle(tiles)
