from collections import namedtuple, OrderedDict
import time
import random
import math

Card = namedtuple('Card', ['colour', 'rank'])
colours = ['red', 'green', 'black']
dragon_rank = -1

dragons = [Card(colour, dragon_rank) for colour in colours for i in range(4)]
normals = [Card(colour, rank) for colour in colours for rank in range(1,9+1)]
flower = Card('flower', 1)

pack = dragons + normals + [flower]
assert len(pack) == 40

def pretty(card, show_empty=False):
    if not card:
        return "--" if show_empty else "  "
    if card.colour == flower:
        return "FL"
    if card.rank == dragon_rank:
        return card.colour[0].upper() * 2
    return card.colour[0] + str(card.rank)

Card.__str__ = pretty
Card.__bool__ = lambda card: bool(card.colour) or bool(card.rank)

def legal_on(card, other):
    if not other:
        return True
    if card.rank == dragon_rank:
        return False
    return other.rank == card.rank + 1 and other.colour != card.colour

def pretty_row(cards, show_empty=False):
    return " ".join(pretty(card, show_empty) for card in cards)

def nth(pile, n):
    try:
        return pile[n]
    except IndexError:
        return Card("", 0)

Move = namedtuple('Move', ['cards', 'source', 'destination'])

def describe_move(move):
    if len(move.cards) == 1:
        cards = "card " + str(move.cards[0])
    else:
        cards = f"cards [{' '.join(str(card) for card in move.cards)}]"
    return f"Move {cards} from {move.source} move to {move.destination}"

Move.__str__ = describe_move

class Board:
    tableau_locations = [f"pile {i}" for i in range(8)]
    cell_locations = [f"cell {i}" for i in range(3)]
    foundation_locations = [f"{colour} foundation" for colour in ['flower'] + colours]

    def __init__(self):
        self.deal()

    def deal(self):
        self.piles = OrderedDict()
        
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
        self.states_seen = set()
        self.history = [str(self)]

    def list_legal_moves(self):
        """List all legal moves."""
        # check first for automatic move and exclude others?
        # prioritise better moves?
        automatic_moves = list(self.list_moves_to_foundation(only_automatic=True))
        if automatic_moves:
            yield from automatic_moves
            return

        yield from self.list_dragon_moves()
        yield from self.list_moves_to_foundation()
        yield from self.list_moves_from_cell_to_tableau()
        yield from self.list_intratableau_moves()
        yield from self.list_moves_from_tableau_to_cell()

    def list_moves_to_foundation(self, only_automatic=False):
        """List moves from cell or tableau to foundation"""
        min_foundation = min(nth(self.piles[loc], -1).rank for loc in self.foundation_locations)
        for source in self.cell_locations + self.tableau_locations:
            card = nth(self.piles[source], -1)
            if not card or card.rank == dragon_rank:
                continue

            destination = f"{card.colour} foundation"
            foundation_card = nth(self.piles[destination], -1)
            if card.rank == 1 or foundation_card.rank == card.rank - 1:
                if not only_automatic or card.rank <= 2 or card.rank <= min_foundation + 1:
                    yield Move([card], source, destination)

    def list_intratableau_moves(self):
        # between tableau moves
        for source in self.tableau_locations:
            pile = self.piles[source]
            for j in reversed(range(len(pile))):
                if j+1 < len(pile) and not legal_on(pile[j+1], pile[j]):
                    continue

                for destination in self.tableau_locations:
                    if source == destination:
                        continue

                    if legal_on(pile[j], self.topmost(destination)):
                        yield Move(pile[j:], source, destination)

    def list_moves_from_cell_to_tableau(self):
        # from cell to tableau topmost
        for source in self.cell_locations:
            if len(self.piles[source]) == 4:
                continue # four dragons

            card = self.topmost(source)
            if not card:
                continue
            for destination in self.tableau_locations:
                if legal_on(card, self.topmost(destination)):
                    yield Move([card], source, destination)

    def list_moves_from_tableau_to_cell(self):
        # from topmost to cell
        first_empty_cell = next(loc for loc in self.cell_locations if not self.piles[loc])
        if first_empty_cell:
            destination = first_empty_cell
            for source in self.tableau_locations:
                card = self.topmost(source)
                if card:
                    yield Move([card], source, destination)

    def list_dragon_moves(self):
        # four dragons to one cell (compound move)
        for colour in colours:
            destination = next(loc for loc in self.cell_locations if not self.piles[loc] or self.topmost(loc).colour == colour and self.topmost(loc).rank == dragon_rank)
            if not destination:
                continue

            sources = [loc for loc in self.cell_locations + self.tableau_locations if self.topmost(loc).colour == colour and self.topmost(loc).rank == dragon_rank]
            if len(sources) == 4:
                yield [Move([self.topmost(source)], source, destination) for source in sources] # special compound move

    def apply_move(self, move, record=True):
        if isinstance(move, (list)):
            for step in move:
                self.apply_move(step, record=False)
        else:
            n = len(move.cards)
            assert self.piles[move.source][-n:] == move.cards
            self.piles[move.source] = self.piles[move.source][:-n]
            # check legality?
            self.piles[move.destination] = self.piles[move.destination] + move.cards

        if record:
            self.move_history.append(move)
            self.history.append(str(self))

    def undo(self):
        """Undo most recent move"""
        move = self.move_history.pop()
        self.history.pop()

        if isinstance(move, list):
            for step in reversed(move):
                self.apply_move(Move(step.cards, step.destination, step.source), record=False)
        else:
            self.apply_move(Move(move.cards, move.destination, move.source), record=False)

    def solve(self, verbose=True):
        """Solve by backtracking"""
        moves = [self.list_legal_moves()]
        self.states_seen.add(self.state())

        while moves:
            try:
                move = next(moves[-1])
            except StopIteration:
                moves.pop(-1)
                if verbose:
                    print("BACKTRACK")
                if self.move_history:
                    self.undo()
                if verbose:
                    print(self)
                continue

            if verbose:
                print(move)

            self.moves_explored += 1
            self.apply_move(move)

            if verbose:
                print(self)
            if self.solved():
                return self.move_history

            if self.state() in self.states_seen:
                moves.append(iter(list()))
                if verbose:
                    print("SEEN BEFORE")
            else:
                moves.append(self.list_legal_moves())
                self.states_seen.add(self.state())


    def solved(self):
        return not(any(self.tableau()))

    def cells(self):
        """List topmost card or None in each cell"""
        return [self.topmost(loc) for loc in self.cell_locations]

    def foundations(self):
        """List topmost card in each foundation"""
        return [nth(self.piles[loc], -1) for loc in self.foundation_locations]

    def tableau(self):
        """List piles in tableau (list of lists)"""
        return [self.piles[loc] for loc in self.tableau_locations]

    def topmost(self, location):
        """List topmost card in given pile"""
        return nth(self.piles[location], -1)

    def state(self):
        cells = pretty_row(sorted(self.cells()))
        tableau = " | ".join(pretty_row(pile) for pile in sorted(self.tableau()))
        return f"cells {cells} tableau {tableau}"

    def __str__(self):
        header = pretty_row(self.cells(), show_empty=True) + "    " + pretty_row(self.foundations(), show_empty=True)

        max_height = max(len(pile) for pile in self.tableau())
        tableau = "\n".join(pretty_row(nth(pile, h) for pile in self.tableau()) for h in range(max_height))

        return "\n" + header + "\n\n" + tableau + "\n"

    def replay(self):
        for screenshot, move in zip(self.history[1:], self.move_history):
            print(move)
            print(screenshot)
            time.sleep(0.5)

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("reps", type=int, default=math.inf, nargs="?")
parser.add_argument("--seed", type=int)
args = parser.parse_args()

if args.seed:
    random.seed(args.seed)

games = list()
i = 0
while i < args.reps:
    i += 1
    board = Board()
    games.append(board)
    print(board)
    if board.solve(verbose=False):
        print(f"Solution in {len(board.move_history)} moves")
    else:
        print("IMPOSSIBLE")
    print(f"Explored {board.moves_explored} moves")
