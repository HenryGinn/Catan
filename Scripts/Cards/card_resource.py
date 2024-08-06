from Cards.card import Card

class CardResource(Card):

    def __init__(self, player, resource):
        super().__init__(player)
        self.resource = resource

