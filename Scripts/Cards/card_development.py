from Cards.card import Card

class CardDevelopment(Card):

    def __init__(self, player, development):
        super().__init__(player)
        self.development = development
