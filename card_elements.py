import random

random.seed(1)

vals_dict = {"J": 11, "Q": 12, "K": 13, "A":1}
class Card:
    
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value
        if value.isnumeric():
            self.numvalue = int(value)
        else:
            self.numvalue = vals_dict[value]
        self.flipped = False
        
    def flip(self):
        self.flipped = not self.flipped
        
    def __str__(self):        
        return f"{self.value} {self.suit}"

    def __gt__(self, other):
        return self.value > other.value

    def __repr__(self):
        return f"{self.value} of {self.suit}"

    
class Pile:
    
    def __init__(self):
        self.cards = []
        
    def addCard(self, Card):
        self.cards.insert(0,Card)
        
    def flipFirstCard(self):
        if self.cards:
            self.cards[0].flip()
            
    def getFlippedCards(self):
        return [card for card in self.cards if card.flipped]
        # return list(itertools.takewhile(lambda x: x.flipped, self.cards))
    
    def __str__(self):
        returnedCards = [str(card) for card in reversed(self.cards) if card.flipped]        
        flippedDownCount = len(self.cards) - len(self.getFlippedCards())
        if flippedDownCount:
            returnedCards.insert(0,"{0} cards flipped down".format(flippedDownCount))
        return ", ".join(returnedCards)

class Deck: 
    
    def __init__(self, values, suits):
        self.cards = []
        self.cache = [] # only here to not break solitaireDONOTCHANGE.py
        self.populate(values,suits)
        self.shuffle()
        
    def __str__(self):
        return ", ".join([str(card) for card in self.cards])

    def populate(self, values, suits):
        #self.cards.extend([Card(suit,value) for suit in suits for value in values])
        for suit in suits:
            for value in values:
                thisCard = Card(suit,value)
                self.cards.append(thisCard)  
    
    def shuffle(self):
        random.shuffle(self.cards)
    
    def getFirstCard(self):
        return self.cards[0] if self.cards else None
    
    def takeFirstCard(self, flip=True):
        if self.cards:
            nextCard = self.cards.pop(0)
            if flip and self.cards:
                self.cards[0].flip()
            return nextCard
        
        
    def drawCard(self):
        if self.cards:
            self.cards[0].flip()
            self.cards.append(self.cards.pop(0))
            self.cards[0].flip()
            
    def sort(self):
        self.cards.sort(reverse=True)
