"""
CS 1, Fall 2020 Final exam part A.

This Module contains some of the Utility functions necessary to run a
game of Cribbage, including functions to make a list of cards to
represent a deck, and check if a list of cards is a valid deck,
is a pair, triplet, or quadruplet, is a straight.

Also has functions to save and load a card deck to and from a file,
and to evaluate the points a user gained by putting the most recent
(highest index) card in a list of cards.
"""

import random
from functools import reduce


DECK_NUM = 52


# Card ranks.
valid_ranks = \
    ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']


# Category codes for cribbage point types.
category_codes = {
    'j': 'initial jack (2 points)',
    'c15': '15 count (2 points)',
    'c31': '31 count (2 points)',
    's3': '3 card straight (3 points)',
    's4': '4 card straight (4 points)',
    's5': '5 card straight (5 points)',
    's6': '6 card straight (6 points)',
    's7': '7 card straight (7 points)',
    'k2': '2 of a kind (2 points)',
    'k3': '3 of a kind (6 points)',
    'k4': '4 of a kind (12 points)'
}


# Order of each rank.
rank_order = {
    'A': 1, '2': 2, '3': 3, '4': 4,
    '5': 5, '6': 6, '7': 7, '8': 8,
    '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13
}


# Point value of each rank.
rank_count = {
    'A': 1, '2': 2, '3': 3, '4': 4,
    '5': 5, '6': 6, '7': 7, '8': 8,
    '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10
}


class InvalidDeck(Exception):
    """Exception class for invalid card decks (ranks only)."""

    pass


def same_ranks(ranks):
    """
    Return `True` if the cards in a list of ranks are all of the same
    rank, false otherwise.
    """

    set_length = len(set(ranks))
    return set_length == 1 or set_length == 0


def is_straight(ranks):
    """Return `True` if the card ranks form a linear sequence.

    A linear sequence means a sequence of consecutive card ranks
    with no gaps.  The rank sequence is: A, 2, 3, ... 10, J, Q, K.
    The order of the cards is unimportant.
    """

    for rank_tup in enumerate(valid_ranks):
        if rank_tup[1] in ranks:
            # We have found the lowest rank in ranks
            lowest_index = rank_tup[0]

            for i in range(lowest_index + 1, lowest_index + len(ranks)):

                if (i >= len(valid_ranks)) or (valid_ranks[i] not in ranks):
                    # Check if the len(ranks)-1 ranks immediatly
                    # higher than the lowest rank are all in ranks.
                    return False

            return True

    return True


def evaluate(stack):
    """Return the number of points gained from the last card
    in the stack.

    Arguments:
    - stack: a list of card ranks

    Return value: a 2-tuple of
    - the points gained from the last card in the stack
    - a list of tags of the cribbage point types from the last card
      in the stack.
    """

    stack_length = len(stack)

    if stack_length == 1 and stack[0] == 'J':
        # If they played the only Jack, they can only get 2 points.
        return (2, ['j'])

    points = 0
    point_tags = []

    # Add points for card count total
    stack_count = reduce(lambda x, y: x + int(rank_count[y]), stack, 0)

    if stack_count == 15 or stack_count == 31:
        points += 2
        point_tags.append("c" + str(stack_count))

    # Add points for pair, triplet or quadruplet
    for i in range(-stack_length, -1):
        if same_ranks(stack[i:]):
            # The points given for n of the same cards is n * (n + 1)
            points += i * (i + 1)
            point_tags.append("k" + str(-i))
            break

    # Add points for any straights 3-7 cards in length, inclusive.
    for i in range(-stack_length, -2):
        if is_straight(stack[i:]):
            points += -i
            point_tags.append("s" + str(-i))
            break

    return (points, point_tags)


def make_deck():
    """Return a shuffled "deck" of 52 cards (ranks only)."""

    deck = valid_ranks * 4
    random.shuffle(deck)

    return deck


def validate_deck(cards):
    """
    Validate a deck of cards (ranks only).

    If the deck is not valid, raise an InvalidDeck exception
    with a meaningful error message.
    """

    if type(cards) is not list:
        raise InvalidDeck(f"Expected a list, got {cards}.")

    cards_length = len(cards)
    if cards_length != DECK_NUM:
        raise InvalidDeck(f"Expected list of length {DECK_NUM}."
                          f" Got list of length {cards_length}.")

    for card in cards:
        if (type(card) is not str) or (card not in valid_ranks):
            raise InvalidDeck(f"Invalid rank in input list: {card}")

    for rank in valid_ranks:
        count = cards.count(rank)

        if count != 4:
            raise InvalidDeck("Expected 4 of each rank."
                              f" There are {count} rank {rank} cards.")


def save_deck(deck, filename):
    """Save a full deck to a file with the name `filename`.

    If the deck is invalid, an InvalidDeck error will be raised."""

    validate_deck(deck)

    # Open file under filename and write. I am allowing the trailing
    # space because my load_deck functionn below can handle this.
    file = open(filename, 'w')

    for card in deck:
        file.write(card + ' ')

    file.close()


def load_deck(filename):
    """Loads an acceptable deck file titled by the string filename
    into a list of ranks and returns the list if it is a valid deck.

    Raises InvalidDeck error if the deck in the file is invalid.
    """

    deck = []

    file = open(filename, 'r')

    for line in file:
        deck += line.strip().upper().split()

    validate_deck(deck)

    file.close()
    return deck
