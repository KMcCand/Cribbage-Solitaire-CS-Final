"""CS1 Final Optional Part C1 | Kyle McCandless

This Module has an autosolver to play the game of Cribbage by
calculating the maximum points it can get in each outcome, looking
a specified number of moves ahead.

Calling: python3 final_partC1.py <deckname> <depth>
<deckname>: the name of the deck to load for Cribbage
<depth>: the number of moves to look ahead. More moves makes the
program slower but more likely to find the maximum possible points.
"""


from final_partB import *
from functools import reduce


DEBUG = False


class RecursiveCribbageSolitaire(CribbageSolitaire):

    def __init__(self):
        CribbageSolitaire.__init__(self)
        self.point_totals = []

    def determine_move(self, max_depth, moves):
        self.point_totals = []
        chosen_depth = min(max_depth, self.num_cards_left())
        self.best_moves(moves, 0, chosen_depth)

        if DEBUG:
            # If debugging, print col # of current move and points
            # the algorithm expects after chosen_depth turns
            print(f"Col #: Points after {chosen_depth} turns:")
            for a in self.point_totals:
                print(f"{a[0]}      {a[1]}")

        max_points = 0
        max_indexes = []

        for i in range(len(self.point_totals)):
            # Find a list of the indices of all maximum possible
            # points in self.point_totals
            this_point_total = self.point_totals[i][1]

            if this_point_total > max_points:
                max_points = this_point_total
                max_indexes = [i]

            elif this_point_total == max_points:
                max_indexes.append(i)

        if DEBUG:
            # If debugging, check that the algorithm's predicted
            # points it will get are the same as what it actually
            # gets
            predictive_points = []
            if self.num_cards_left() <= max_depth:
                predictive_points.append(max_points)
            if self.num_cards_left() == 1:
                for end_points in predictive_points:
                    assert end_points == self.points
                    print("Passing end point total asserts...")

        # Choose move randomly from moves that get max points
        return self.point_totals[random.choice(max_indexes)][0]

    def autoplay(self, max_depth, verbose=True, pause=False):
        """Automatically play a game until finished, using the
        autosolver that can look max_depth moves ahead.

        Argument:
        - verbose: if `True`, print extra information after a move
        - pause: if `True`, pause after printing move info.

        Return value: none
        """

        while not self.game_over():
            self.dump()
            moves = self.legal_moves()
            print(f'MOVES: {moves}')

            if not moves:
                print('No moves; starting a new stack...')
                # empty the stack, zero the count
                self.stack = []
                self.count = 0
                continue

            move = self.determine_move(max_depth, moves)

            print(f'MOVE: {move}')
            codes = self.make_move(move)
            if codes and verbose:
                print(f'Stack after move: {self.stack}')
                for code in codes:
                    print(f'+++ {category_codes[code]}')
            if pause:
                self.pause()

        self.dump()
        print(f'TOTAL POINTS: {self.points}')
        self.win_or_lose()
        self.save_moves('moves.out')

    def num_cards_left(self):
        """Takes no arguments. Returns the number of cards in self.cols."""

        return reduce(lambda x, y: x + len(y), self.cols, 0)

    def best_moves(self, moves, depth, max_depth):
        """Arguments:
        moves - a list of column indices 0-3 that are legal in the
        current game state
        depth - the amount of moves in the future the algorithm is
        currently looking
        max_depth - the maximum amount of moves in the future the
        algorithm should consider to make a move

        Appends all possible first moves and the point values they
        lead to max_depth moves in the future to self.point_totals.
        """

        if depth == max_depth:
            # For every possible outcome, append the first column
            # number moved and the future resultant points to storage
            first_column = self.history[-max_depth][1]
            future_points = self.history[-1][4]

            self.point_totals.append((first_column, future_points))

        else:

            if not moves:
                self.stack = []
                self.count = 0
                moves = self.legal_moves()

            for col_index in moves:
                # For every legal move, do the move then see what the
                # best moves are in this new state, then undo the move
                # to keep game state the same
                self.make_move(col_index)
                self.best_moves(self.legal_moves(), depth + 1, max_depth)
                self.undo_move()


if __name__ == '__main__':
    args = sys.argv[1:]
    cs = RecursiveCribbageSolitaire()

    args_length = len(args)

    if args_length != 2:
        print(f"Error: Expected two command line args, got {args_length}.")
        quit(1)

    try:
        depth = int(args[1])
    except ValueError as e:
        print(f"Entered depth caused an error: {e}")
        quit(1)

    if depth < 1:
        raise TypeError(f"Expected depth >= 1, got {depth}.")

    try:
        cs.load(args[0])
    # No matter the type of exception, the only specificity on
    # top of the error message is that it was due to the filename
    except Exception as e:
        print(f"Entered filename caused an error: {e}")
        quit(1)

    cs.autoplay(depth)
