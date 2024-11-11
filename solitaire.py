from card_elements import Card, Deck, Pile
from codecarbon import EmissionsTracker
import pprint
import random

random.seed(0)
pp = pprint.PrettyPrinter(indent=4)

with EmissionsTracker() as tracker:

    class Game:
        list_of_values = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
        colors = ["red", "black"]
        signs = ["diamond", "spades", "hearts", "clubs"]

        # output = []
        # for i in list_of_values:
        #     for x in signs:
        #         for y in colors:
        #             output.append(f"Card: {i} Color: {y} Symbol: {x}")
        # print("The cards in your deck are:", "".join(output))

        suits = {  # keys are unicode symbols for suits
            u'\u2660': "black",
            u'\u2665': "red",
            u'\u2663': "black",
            u'\u2666': "red",
        }

        numPlayPiles = 7

        def __init__(self):
            self.deck = Deck(self.list_of_values, self.suits)
            self.playPiles = []
            for i in range(self.numPlayPiles):
                thisPile = Pile()
                [thisPile.addCard(self.deck.takeFirstCard(flip=False)) for j in range(i + 1)]
                thisPile.flipFirstCard()
                self.playPiles.append(thisPile)
            self.blockPiles = {suit: Pile() for suit in self.suits}
            self.deck.cards[0].flip()

        def getGameElements(self):
            returnObject = {
                "deck": str(self.deck),
                "playPiles": [str(pile) for pile in self.playPiles],
                "blockPiles": {suit: str(pile) for suit, pile in self.blockPiles.items()}
            }
            return returnObject

        def checkCardOrder(self, higherCard, lowerCard):
            if higherCard.suit == lowerCard.suit:
                return False
            return higherCard.numvalue - 1 == lowerCard.numvalue

        def checkIfCompleted(self):
            # if deck is not empty, game not over
            if not self.deck.cards:
                return False
            
            for pile in self.playPiles:
                if pile.cards:
                    return False

            for pile in self.blockPiles.values():
                if len(pile.cards) != 13:
                    return False
            return True

        def addToBlock(self, card):
            if card is None:
                return False

            suitBlock = self.blockPiles[card.suit].cards
            if suitBlock:
                if suitBlock[0].numvalue + 1 == card.numvalue:
                    self.blockPiles[card.suit].cards.insert(0, card)
                    return True
                else:
                    return False
            else:
                if card.numvalue == 1:
                    self.blockPiles[card.suit].cards.insert(0, card)
                    return True
                else:
                    return False

        def pileToBlock(self):
            # 1: check if there are any play pile cards you can play to block piles
            for pile in self.playPiles:
                if pile.cards and self.addToBlock(pile.cards[0]):
                    pile.cards.pop(0)
                    return True
            return False

        def deckToBlock(self):
            # 2: check if cards in deck can be added
            if self.addToBlock(self.deck.getFirstCard()):
                self.deck.takeFirstCard()
                return True
            return False

        def kingToEmptyPile(self):
            for pile in self.playPiles:
                if pile.cards: # pile must be empty
                    continue
                for pile2 in self.playPiles:
                    if len(pile2.cards) > 1 and pile2.cards[0].numvalue == 13:
                        card_added = pile2.cards.pop(0)
                        pile.addCard(card_added)
                        return True

                if self.deck.getFirstCard() is not None and self.deck.getFirstCard().numvalue == 13:
                    card_added = self.deck.takeFirstCard()
                    pile.addCard(card_added)
                    return True
            return False

        def deckToPlayPile(self):
            # 4: add drawn card to playPiles
            for pile in self.playPiles:
                if pile.cards and self.deck.getFirstCard() is not None:
                    if self.checkCardOrder(pile.cards[0], self.deck.getFirstCard()):
                        card_added = self.deck.takeFirstCard()
                        pile.addCard(card_added)
                        return True
            return False

        def movePlayPiles(self):
            """
            Move cards to piles with less downward facing cards
            """
            for source_pile in self.playPiles:
                source_flipped_cards = source_pile.getFlippedCards()

                if not source_flipped_cards:
                    continue
                for target_pile in self.playPiles:
                    if source_pile is target_pile:
                        continue
                    target_flipped_cards = target_pile.getFlippedCards()
                    if not target_flipped_cards:
                        continue
                    for transfer_cards_size in range(1, len(source_flipped_cards) + 1):
                        cards_to_transfer = source_flipped_cards[:transfer_cards_size]
                        if not self.checkCardOrder(target_pile.cards[0], cards_to_transfer[-1]):
                            continue
                        source_downcard_count = len(source_pile.cards) - len(source_flipped_cards)
                        target_downcard_count = len(target_pile.cards) - len(target_flipped_cards)
                        if target_downcard_count < source_downcard_count:
                            target_pile.cards[0:0] = cards_to_transfer
                            source_pile.cards = source_pile.cards[transfer_cards_size:]
                            return True
                        elif source_downcard_count == 0 and len(cards_to_transfer) == len(source_pile.cards):
                            target_pile.cards[0:0] = cards_to_transfer
                            source_pile.cards = []
                            return True
            return False


        def takeTurn(self):
            # Pre: flip up unflipped pile end cards -> do this automatically
            [pile.cards[0].flip() for pile in self.playPiles if pile.cards and not pile.cards[0].flipped]

            # 1: check if there are any play pile cards you can play to block piles
            if self.pileToBlock():
                return True

            # 2: check if cards in deck can be added
            if self.deckToBlock():
                return True

            # 3: check if you can move a king to an empty pile
            if self.kingToEmptyPile():
                return True

            # 4: add drawn card to playPiles
            if self.deckToPlayPile():
                return True

            # 5: move around cards in playPiles
            if self.movePlayPiles():
                return True
            return False
        
        
        def simulate(self, draw=False):
            """
            Simulates the game using iteration instead of recursion.
            Returns when no more moves are possible.
            """
            cache = set()
            while True:
                # Clear cache if last turn was not card draw
                if not draw:
                    cache = set()
                    
                # Take turn and check if any moves were made
                if self.takeTurn():
                    draw = False
                    continue
                    
                # No moves possible - try drawing from deck
                if not self.deck.cards:
                    return
                    
                current_card = self.deck.cards[0]
                
                # Check if we've seen this card before in this sequence
                if current_card in cache:
                    return
                    
                # Draw new card and continue
                self.deck.drawCard()
                cache.add(current_card)
                draw = True

        def sort_deck(self):
            self.deck.sort()


    def main():
        thisGame = Game()
        thisGame.simulate()
        pp.pprint(thisGame.getGameElements())
        if (thisGame.checkIfCompleted()):
            print("Congrats! You won!")
        else:
            print("Sorry, you did not win")

        thisGame.sort_deck()
        print("Sorted cards:", thisGame.deck)
        return

    main()
