from collections import namedtuple, OrderedDict
import random
Card = namedtuple('Card', ['colour', 'rank'])
colours = ['red', 'green', 'black']

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
Card.__bool__ = lambda card: bool(card.colour) or bool(card.rank)

def legal_on(card, other):
    if not other:
        return True
    if card.rank == "dragon":
        return False
    return other.rank == card.rank + 1 and other.colour != card.colour

def pretty_row(cards, show_empty=False):
    return " ".join(pretty(card, show_empty) for card in cards)

def nth(pile, n):
    try:
        return pile[n]
    except IndexError:
        return Card(None, None)

Move = namedtuple('Move', ['cards', 'source', 'destination'])

class Board:
    tableau_locations = [f"pile {i}" for i in range(8)]
    cell_locations = [f"cell {i}" for i in range(3)]
    foundation_locations = [f"{colour} foundation" for colour in ['flower'] + colours]

    def __init__(self):
        self.deal()

    def deal(self):
        self.piles = dict()
        
        random.shuffle(pack)
        tableau = [pack[5*i:5*(i+1)] for i in range(8)]
        for loc, cards in zip(self.tableau_locations, tableau):
            self.piles[loc] = cards

        for loc in self.cell_locations:
            self.piles[loc] = []

        for loc in self.foundation_locations:
            self.piles[loc] = []

        self.move_history = list()
        self.moves_explored = 0

    def list_legal_moves(self):
        # from cell or tableau topmost to foundation
        for source in self.cell_locations + self.tableau_locations:
            card = nth(self.piles[source], -1)
            if not card or card.rank == "dragon":
                continue

            destination = f"{card.colour} foundation"
            foundation_card = nth(self.piles[destination], -1)
            if card.rank == 1 or foundation_card.rank == card.rank - 1:
                yield Move([card], source, destination)

        # between foundations
        for source in self.tableau_locations:
            pile = self.piles[source]
            for j in reversed(range(len(pile))):
                if j+1 < len(pile) and not legal_on(pile[j], pile[j+1]):
                    continue

                for destination in self.tableau_locations:
                    if source == destination:
                        continue

                    if legal_on(pile[j], self.topmost(destination)):
                        yield Move(pile[j:], source, destination)

        # four dragons to one cell (compound move)
        for colour in colours:
            pass
            # yield []

        # from cell to topmost
        # from topmost to cell
        # group from one pile to another

    def apply_move(self, move, record=True):
        n = len(move.cards)
        assert self.piles[move.source][-n:] == move.cards
        self.piles[move.source] = self.piles[move.source][:-n]
        self.piles[move.destination] = self.piles[move.destination] + move.cards
        if record:
            self.move_history.append(move)

    def undo(self):
        """Undo most recent move"""
        move = self.move_history.pop()
        self.apply_move(Move(move.cards, move.destination, move.source), record=False)

    def solve(self):
        """Solve by backtracking"""
        if self.solved():
            return self.move_history

        # how to avoid infinite loops? record past state?

        for move in self.list_legal_moves():
            print(move)
            self.moves_explored += 1
            self.apply_move(move)
            print(self)
            success = self.solve()
            if success:
                return success
            print("BACKTRACK")
            self.undo()
            print(board)

    def solved(self):
        return not(any(self.cells())) and not(any(self.tableau()))

    def cells(self):
        """List topmost card or None in each cell"""
        cell_piles = [self.piles[loc] for loc in self.cell_locations]
        assert all(len(pile) <= 1 for pile in cell_piles)
        return [nth(pile, -1) for pile in cell_piles]

    def foundations(self):
        """List topmost card in each foundation"""
        return [nth(self.piles[loc], -1) for loc in self.foundation_locations]

    def tableau(self):
        """List piles in tableau (list of lists)"""
        return [self.piles[loc] for loc in self.tableau_locations]

    def topmost(self, location):
        """List topmost card in given pile"""
        return nth(self.piles[location], -1)

    def __str__(self):
        header = pretty_row(self.cells(), show_empty=True) + "    " + pretty_row(self.foundations(), show_empty=True)

        max_height = max(len(pile) for pile in self.tableau())
        tableau = "\n".join(pretty_row(nth(pile, h) for pile in self.tableau()) for h in range(max_height))

        return header + "\n\n" + tableau + "\n"

board = Board()
print(board)
board.solve()
print()
print(board.moves_explored)