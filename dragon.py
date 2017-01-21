from collections import namedtuple, OrderedDict
import random

Card = namedtuple('Card', ['colour', 'rank'])
colours = ('red', 'green', 'black')

dragons = [Card(colour, "dragon") for colour in colours for i in range(4)]
normals = [Card(colour, rank) for colour in colours for rank in range(1,9+1)]
flower = Card('flower', 1)

pack = dragons + normals + [flower]
assert len(pack) == 40

def pretty(card, show_empty=False):
    if not card:
        return "--" if show_empty else "  "
    if card.colour == flower:
        return "FL"
    if card.rank == "dragon":
        return card.colour[0].upper() * 2
    return card.colour[0] + str(card.rank)

Card.__str__ = pretty

def pretty_row(cards, show_empty=False):
    return " ".join(pretty(card, show_empty) for card in cards)

def nth(pile, n):
    try:
        return pile[n]
    except IndexError:
        return None

class Board:
    def __init__(self):
        self.deal()

    def deal(self):
        random.shuffle(pack)
        self.tableau = tuple(pack[5*i:5*(i+1)] for i in range(8))
        self.cells = [None, None, None]
        self.foundations = OrderedDict((colour, []) for colour in [flower]+list(colours))

    def list_moves(self):
        pass

    def solve(self):
        pass

    def __str__(self):
        header = pretty_row(self.cells, show_empty=True) + "    " + pretty_row([nth(foundation, -1) for foundation in self.foundations.values()], show_empty=True)

        max_height = max(len(pile) for pile in self.tableau)
        tableau = "\n".join(pretty_row(nth(pile, h) for pile in self.tableau) for h in range(max_height))

        return header + "\n\n" + tableau

board = Board()
print(board)