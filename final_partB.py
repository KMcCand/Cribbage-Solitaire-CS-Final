"""
CS 1, Fall 2020 Final exam part B.

This Module, along with the utility functions in the Module
final_partA.py, runs a game of Cribbage, either for one player to
maximize their score ona random deck or a deck read in from a file,
or for a computer player to do the same.

Includes a CribbageSolitaire class that stores the state of the game,
has methods to make a move, load a deck from a file, save a deck, and
run the game.

Optional Command line arguments:
 - If no input command line args, runs game for user with random deck
 - If "autoplay" entered, runs game with 1 move look ahead autosolver
 on random deck
 - If "replay" and <filename> entered, runs game for user by loading
 the deck found at filename
 - If "autoreplay" and <filename>, runs 1 move look ahead autosolver
 for the deck found at filename
"""

import random
import sys


from final_partA import *


class InvalidMove(Exception):
    """Exception class raised when an invalid move is attempted."""

    pass


class CribbageSolitaire:
    """Cribbage Solitaire interactive player and autosolver."""

    def __init__(self):
        """Initialize this object."""
        deck = make_deck()
        save_deck(deck, 'deck.out')

        self.cols = [deck[:13], deck[13:26], deck[26:39], deck[39:]]
        self.stack = []
        self.count = 0
        self.points = 0
        self.history = []

    def __str__(self):
        """Convert the layout to a string for printing."""
        s = '\n   0  1  2  3\n'
        s += '+-------------+\n'
        for i in range(13):
            s += '| '
            for col in range(4):
                if len(self.cols[col]) > i:
                    contents = self.cols[col][i]
                else:
                    contents = '  '
                s += f'{contents:>2s} '
            s += '|\n'
        s += '+-------------+\n'
        return s

    def load(self, filename):
        """
        Load a deck from a file.

        Read the deck's card ranks from the file,
        validate the deck, use it to initialize the columns,
        and reset the other fields of the object.

        Arguments:
        - filename: the name of the deck file to load

        Return value: none
        """

        deck = load_deck(filename)
        validate_deck(deck)

        # NOTE: Does not shuffle deck from filename before storing
        self.cols = [deck[:13], deck[13:26], deck[26:39], deck[39:]]

        # Reset other fields to values initialized by constructor
        self.stack = []
        self.count = 0
        self.points = 0
        self.history = []

    def legal_moves(self):
        """
        Return a list of column indices of all legal moves.

        The returned move list should be sorted in ascending order.
        """

        legal = []

        for i in range(0, 4):
            this_col = self.cols[i]

            if this_col and self.count + rank_count[this_col[-1]] <= 31:
                # If the count of stack with the last card in this_col
                # added is <= 31, add this_col's index to legal moves
                legal.append(i)

        return legal

    def make_move(self, i):
        """
        Play the bottom card of column `i`.

        Add the points gained from playing the card.
        Save undo information.
        Raise `InvalidMove` if
        * the column index is invalid
        * the column is empty
        * the move can't be made without making the count go above 31.

        Arguments:
        - i: the column index

        Return value:
        - the list of category codes which represent
          the card configurations achieved by playing this card

        Assumption:
            This method assumes that `i` represents the index
            of a non-empty column whose last card can legally
            be played.
        """

        # Raise InvalidMove if column index invalid, empty column, or
        # move makes count > 31
        if type(i) is not int:
            raise InvalidMove("The input column index was not an integer.")
        elif i < 0 or i > 3:
            raise InvalidMove(f"Expected column between 0 and 3. Got {i}.")
        elif not self.cols[i]:
            raise InvalidMove(f"The column at index {i} is empty!")
        elif i not in self.legal_moves():
            raise InvalidMove(f"This move would make stack {i}'s count > 31!")

        moved = self.cols[i].pop()

        # Append current game state to history list
        self.history.append((moved, i, self.stack[:], self.count, self.points))

        # Make the move
        self.stack.append(moved)

        # Update stack count
        self.count += rank_count[moved]

        # Update points and return category codes in list of strings
        points_tup = evaluate(self.stack)
        self.points += points_tup[0]
        return points_tup[1]

    def undo_move(self):
        """Undo the last move, restoring the previous state."""

        if self.history:
            undid_move = self.history.pop()

            # Add undid_move card to the column it got moved from and
            # update stack
            self.cols[undid_move[1]].append(undid_move[0])
            # I think it might be a little dangerous not to make a copy
            # of undid_move[2], however undid_move is not going to be
            # edited again so I think its ok to save efficiency
            self.stack = undid_move[2][:]

            # Undo affect of undid_move on count and points
            self.count = undid_move[3]
            self.points = undid_move[4]

    def save_moves(self, filename):
        """
        Save the moves of a game (column indices) to a file.

        Arguments:
        - filename: the name of the file to save the moves to.

        Return value: none
        """

        file = open(filename, 'w')

        for i in range(0, len(self.history)):
            file.write(f"{self.history[i][1]} ")

            if i % 4 == 3:
                # If this print is the fourth in one line,
                # go to next line
                file.write("\n")

        file.close()

    def best_moves(self, moves):
        """
        Return the best of a list of moves.

        The "best" move is the one that, when played, improves the
        score the most.  There can be more than one such move.
        If no move improves the score, or if all moves improve the
        score by the same amount, return the entire list.

        This method assumes that the list of moves
        doesn't contain an illegal move.

        The game state is not changed by this method.

        Arguments:
        - moves: a list of moves (column indices)

        Return value: a list of the best moves
        """

        if len(moves) <= 1:
            return moves

        best_list = []
        highest_points = 0

        for col_index in moves:
            self.make_move(col_index)

            if self.points > highest_points:
                # We have found a best move better than those
                # previously found
                best_list = [col_index]
                highest_points = self.points

            elif self.points == highest_points:
                # We have found a best move equal to those previously
                # found
                best_list.append(col_index)

            self.undo_move()

        return best_list

    def get_move(self, moves):
        """
        Interactively pick one of a set of legal moves.

        Argument:
        - moves: a list of ints representing all legal moves

        Return value: one of
        - one of the list of ints
        - the string 'q' (for "quit")
        - the string 'u' (for "undo")
        """
        print(f'Legal moves: {moves}')
        move = None
        while move not in moves:
            move = input('Enter move: ')
            # Handle one-character special "moves".
            if move in ['q', 'u']:
                return move
            try:
                move = int(move)
                if move not in moves:
                    print(f'Error: move {move} is not in ' +
                          f'list of moves {moves}')
                    move = None
            except ValueError:
                print('Error: invalid move entered.')
                move = None
        return move

    def game_over(self):
        """Return `True` if the game is over."""
        return self.cols == [[], [], [], []]

    def dump(self):
        """Print information about the current game."""
        print(self)
        print(f'STACK: {self.stack}')
        print(f'POINTS: {self.points}')
        print(f'COUNT: {self.count}')
        print()

    def win_or_lose(self):
        """Print a message telling whether the player won or lost."""
        if self.game_over():
            if self.points >= 61:
                print('You win!  Congratulations, well played!')
            else:
                print('Sorry, you lose.  Better luck next time.')
        else:
            print('The game is not over yet.  Keep playing!')

    def pause(self):
        """
        Pause so user can read the output.

        The user hits the return key to continue.
        If the user enters the 'q' key, the program exits.
        """
        while True:
            answer = input('Press <return> to continue... ')
            if answer == '':
                break
            elif answer == 'q':
                quit()

    def autoplay(self, verbose=True, pause=False):
        """Automatically play a game until finished.

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
            best = self.best_moves(moves)
            move = random.choice(best)
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

    def play(self):
        """Interactively play a game until finished."""
        while not self.game_over():
            self.dump()
            moves = self.legal_moves()
            if not moves:
                # empty the stack, zero the count
                print('No moves; starting a new stack...')
                self.stack = []
                self.count = 0
                self.pause()
                continue
            move = self.get_move(moves)
            if move == 'q':
                return
            elif move == 'u':
                if self.history == []:
                    print('no history to undo!')
                else:
                    print('undoing last move...')
                    self.undo_move()
            else:
                codes = self.make_move(move)
                if codes:
                    print(f'Stack after move: {self.stack}')
                    for code in codes:
                        print(f'+++ {category_codes[code]}')
        self.dump()
        print(f'TOTAL POINTS: {self.points}')
        self.win_or_lose()
        self.save_moves('moves.out')


if __name__ == '__main__':
    try:
        args = sys.argv[1:]
        cs = CribbageSolitaire()
        if len(args) == 0:
            cs.play()
        elif len(args) == 1 and args[0] == 'autoplay':
            cs.autoplay(verbose=True, pause=True)
        elif len(args) == 2 and args[0] == 'replay':
            cs.load(args[1])
            cs.play()
        elif len(args) == 2 and args[0] == 'autoreplay':
            cs.load(args[1])
            cs.autoplay()
    except InvalidDeck as e:
        print(f'Error (invalid deck): {e}')
        quit(1)
