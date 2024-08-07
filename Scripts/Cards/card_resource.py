from Cards.card import Card

class CardResource(Card):

    category = "Resource"
    
    def __init__(self, player, resource):
        super().__init__(player)
        self.name = resource

