"""CS1 Final Optional Part C2 | Kyle McCandless

This Module runs a game of Cribbage Soletaire as in final_partB,
but using tkinter to make a GUI. Runs the game for a user and a
random deck only.

Includes a CribbageSolitaireGUI class that inherits from
CribbageSolitaire layed out in final_partB and includes methods to
display all of the cards, the users points, any special point
comboinations they made, and whether they won or lost.

General Reference Source: (The first was used to learn the basic of
labels, texts, images, and buttons, the second to learn .place as
.pack was not working, and the third was to delay actions in tkinter,
the .after method)
https://robotic-controls.com/book/export/html/7

https://pythonbasics.org/tkinter-image/

https://stackoverflow.com/questions/23381319/
make-a-button-appear-after-some-time

More specific reference sources are linked in the comments next to
where they are used.
"""


from final_partB import *
import tkinter as tk
import random
import time


# The folder the all of the programs images are stored in.
# Images must be .gif files because of tkinter PhotoImage limitations
IMAGE_DIRECTORY = "GUI_Images"


class CribbageSolitaireGUI(CribbageSolitaire):

    def __init__(self):
        """Initialize this object."""

        deck = make_deck()

        self.cols = [deck[:13], deck[13:26], deck[26:39], deck[39:]]
        self.stack = []
        self.count = 0
        self.points = 0
        self.history = []

        self.card_labels = [[], [], [], []]
        self.stack_labels = []

        self.bottom_coords = []
        for i in range(4):
            self.bottom_coords.append((513, 661))

    def display_cards(self):
        """Clear all the previous cards displayed by this method, then
        display the cards in self.cols in 4 columns. Have the cards
        overlap, but not enough that their numbers get blocked. Update
        self.bottom_coords to have 4 tuples of the top and bottom
        coordinates respectively of the 4 lowest cards.
        """

        for card_label_list in self.card_labels:
            for card_label in card_label_list:
                # Destroy all the previous cards that were displayed
                card_label.destroy()

        # Get rid of all the destroyed cards' labels
        self.card_labels = [[], [], [], []]

        height = 0
        width = 0

        # Display all the cards:
        for i in range(4):
            this_col_len = len(cs.cols[i])

            for j in range(this_col_len):
                card_name = cs.cols[i][j]

                try:
                    card = tk.PhotoImage(
                        file=f"{IMAGE_DIRECTORY}/{card_name}.gif").subsample(7)
                except FileNotFoundError:
                    print("Failed to find the card image"\
                        f"associated with {card_name}.")
                    quit(1)

                width = card.width()
                height = card.height()

                card_label = tk.Label(
                                  root, width=width, height=height, image=card,
                                  borderwidth=0, bg="forest green")
                # Need to anchor poop to card_label so that
                # Garbage Collection doesn't make it go away.
                # Got help with this from Stack Overflow:
                # https://stackoverflow.com/questions/16424091/why-
                # does-tkinter-image-not-show-up-if
                # -created-in-a-function
                card_label.photo = card

                card_label.place(x=105 * i + 30, y=40 * j + 30)

                # Update self.card_labels
                self.card_labels[i].append(card_label)

            # Update bottom_coords
            lowest_card_top = 40 * (this_col_len - 1) + 30
            self.bottom_coords[i] = (lowest_card_top, lowest_card_top + height)

    def display_numbers(self):
        """Display the count of the current stack and the
        user's total points so far in the top right corner.
        """

        points_str = str(self.points)

        # Calculate the total space between the headings
        total_space = int(root.winfo_width() / 100)

        # Calculate the space between each heading and its number
        small_space = int(total_space / 3)

        # Calculate remaining space between the number for
        # "Total Points" and the "Stack Count" heading. Subtract two
        # because "Points:" is two chars longer than "Total".
        remaining_space = (total_space - len(points_str) - small_space - 2)

        text_string = ("Total" + " " * total_space + "Stack\nPoints:"
                       + " " * small_space + points_str + " " * remaining_space
                       + "Count:" + " " * small_space + str(self.count))

        # Create text with text_string
        points_text = tk.Text(root, bg="forest green", font=(
            "Courier", 20), pady=50, highlightthickness=0, height=100)
        points_text.insert("1.0", text_string)
        points_text.place(x=480, y=0)

    def display_stack(self):
        """Clear the previous stack displayed by this method, then
        display the current stack under the heading "Your Stack"."""

        stack_text = tk.Text(root, bg="forest green", font=(
            "Courier", 20), highlightthickness=0, height=600)
        stack_text.insert("1.0", "Your Stack:")
        stack_text.place(x=480, y=110)

        for stack_label in self.stack_labels:
            # Destory all the previous cards in stack
            stack_label.destroy()

        # Get rid of all previous cards' labels
        self.stack_labels = []

        for index_card_tup in enumerate(self.stack):
            index = index_card_tup[0]
            card = index_card_tup[1]

            try:
                card = tk.PhotoImage(
                    file=f"{IMAGE_DIRECTORY}/{card}.gif").subsample(7)
            except FileNotFoundError:
                print(f"Failed to find the card image associated with {card}.")
                quit(1)

            height = card.height()

            card_label = tk.Label(root, height=height,
                                  image=card, borderwidth=0, bg="forest green")
            
            # Need to anchor poop to card_label so that
            # Garbage Collection doesn't make it go away.
            # Got help with this from Stack Overflow:
            # https://stackoverflow.com/questions/16424091/why-
            # does-tkinter-image-not-show-up-if
            # -created-in-a-function
            card_label.photo = card

            card_label.place(x=480, y=40 * index + 140)

            # Update self.stack_labels
            self.stack_labels.append(card_label)

    def legal_moves(self):
        """Return a list of column indices of all legal moves
        sorted in ascending order.
        """

        legal = []

        for i in range(0, 4):
            this_col = self.cols[i]

            if this_col and self.count + rank_count[this_col[-1][:-1]] <= 31:
                # If the count of stack with the last card in this_col
                # added is <= 31, add this_col's index to legal moves
                legal.append(i)

        return legal

    def make_move(self, i):
        """
        Play the bottom card of column `i`. Same as make_move from
        final_partB, but adapted to allow cards with two or three
        chracter long names.

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
        self.count += rank_count[moved[:-1]]

        # Update points and return category codes in list of strings
        points_tup = evaluate(self.stack)
        self.points += points_tup[0]

        return points_tup[1]

    def display_all(self):
        """Display the whole board."""

        self.display_cards()
        self.display_numbers()
        self.display_stack()

    def play(self):
        """Clear the welcome screen (leaving the background green),
        then display the board.
        """

        # Clear welcome screen
        for child in root.winfo_children():
            child.destroy()

        self.display_all()

    def do_move(self, i):
        """Make the move visually by taking the bottom card of
        column i.

        Return False if this move is illegal and there are other legal
        moves, else return True.
        """

        if i in self.legal_moves():

            display_codes(self.make_move(i))

            if self.cols == [[], [], [], []]:
                end_game(self.points)

            # Display the board
            self.display_all()

            if not self.legal_moves():
                # If there are no moves, empty the stack and zero the count
                self.empty_stack()

            return True

        else:
            # If there are moves, and the user's choice i is not one of
            # the legal moves, return False
            return False

    def empty_stack(self):
        """Inform the user that the stack is being emptied by printing
        in the lower left corner of the screen. Set the internal stack
        to empty and the count to 0.
        """

        self.stack = []
        self.count = 0

        text = tk.Text(root, bg="forest green", font=(
                                  "Courier", 20, "bold"), highlightthickness=0)
        text.place(x=50, y=700)
        text.insert("1.0", "Stack is full. Emptying stack")

        for i in range(6):
            # Print an expanding line of dots after the message
            root.update()
            root.after(250, text.insert("4.0", "."))

        text.destroy()

        # Redisplay the stack and numbers because they have changed
        self.display_stack()
        self.display_numbers()

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

            self.display_all()

        else:
            no_undos()


def make_deck():
    """Return a shuffled "deck" of 52 cards, including suits,
    of the form [Rank][Suit] where Suit is H, D, S, or C.
    """

    suits = ['H', 'D', 'S', 'C']
    deck = []

    for i in range(4):
        for rank in valid_ranks:
            deck.append(rank + suits[i])

    random.shuffle(deck)

    return deck


def same_ranks(ranks):
    """
    Return `True` if the cards in a list of ranks are all of the same
    rank, false otherwise. Ignore the last character of the cards
    because this specifies their suit.
    """

    ranks_set = set()
    for card in ranks:
        ranks_set.add(card[:-1])

    set_len = len(ranks_set)
    return set_len == 1 or set_len == 0


def is_straight(ranks):
    """Return `True` if the card ranks form a linear sequence.

    Get rid of the last character of every element of ranks
    because this represents the suit.

    A linear sequence means a sequence of consecutive card ranks
    with no gaps.  The rank sequence is: A, 2, 3, ... 10, J, Q, K.
    The order of the cards is unimportant.
    """

    for i in range(len(ranks)):
        ranks[i] = ranks[i][:-1]

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
    in the stack. Same as evaluate from final_partB, except
    adapted for cards having two or three character long names.

    Arguments:
    - stack: a list of card ranks

    Return value: a 2-tuple of
    - the points gained from the last card in the stack
    - a list of tags of the cribbage point types from the last card
      in the stack.
    """

    stack_length = len(stack)

    if stack_length == 1 and stack[0][:-1] == 'J':
        # If they played the only Jack, they can only get 2 points.
        return (2, ['j'])

    points = 0
    point_tags = []

    # Add points for card count total
    stack_count = reduce(lambda x, y: x + int(rank_count[y[:-1]]), stack, 0)

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

    return points, point_tags


def end_game(points):
    """Ends the game by informing the user if they won or lost."""

    end_text = tk.Text(root, bg="forest green", font=(
        "Courier", 30), highlightthickness=0)
    end_text.place(x=20, y=700)

    if points >= 61:
        end_text.insert("1.0", f"You Won!!!!!! ({points} points)")
    else:
        end_text.insert("1.0", f"You lost :(( ({points} points)")

    poop_text = tk.Text(root, bg="forest green", font=(
        "Courier", 15), highlightthickness=0)
    poop_text.place(x=20, y=730)
    poop_text.insert("1.0", "\nPress 'p' for a poop emoji, or q to quit.")


def no_undos():
    """Inform the user that there are no moves to undo by printing
    a message in the bottom left corner.
    """

    no_undo_text = tk.Text(
        root, bg="forest green", font=("Courier", 20), highlightthickness=0)
    no_undo_text.place(x=50, y=700)
    no_undo_text.insert("1.0", "There are no moves to undo.")

    # Display the text then make it go away after 1.5 seconds
    root.update()
    root.after(1500, no_undo_text.destroy())
    root.update()


def display_codes(codes):
    """Display the codes to the points that the user got for three
    seconds in red font, then remove them.
    """

    codes_dict = {
        'j': '* Initial Jack - 2 points *',
        'c15': '* Count of 15 - 2 points *',
        'c31': '* Count of 31 - 2 points *',
        's3': '* 3 Card Straight - 3 points *',
        's4': '* 4 Card Straight - 4 points *',
        's5': '* 5 Card Straight! - 5 points *',
        's6': '* 6 Card Straight!! - 6 points *',
        's7': '* 7 Card Straight!!!! - 7 points *',
        'k2': '* 2 of a Kind - 2 points *',
        'k3': '* 3 of a Kind! - 6 points *',
        'k4': '* 4 of a Kind!!! - 12 points *'
    }

    points_text = tk.Text(root, bg="forest green", font=(
        "Courier", 30, "bold"), highlightthickness=0, fg="blue")
    points_text.place(x=50, y=700)

    for code in codes:
        points_text.insert("1.0", codes_dict[code] + "\n")

    if codes:
        # Make the code go yellow then red then blue
        for i in range(3):
            root.update()
            root.after(200, points_text.configure(fg="yellow"))
            root.update()
            root.after(200, points_text.configure(fg="red"))
            root.update()
            root.after(200, points_text.configure(fg="blue"))

        points_text.destroy()


def key_handler(event):
    if event.keysym == 'q':
        quit()

    elif event.keysym == 'p':
        poop_label = place_poop()

    elif event.keysym == 'u':
        cs.undo_move()


def click_handler(event):
    """Handle clicks by moving the card clicked to stack if it is
    a valid move.
    """

    x_coord = event.x_root
    y_coord = event.y_root

    for i in range(4):
        this_coord_tup = cs.bottom_coords[i]
        card_bottom = this_coord_tup[1]

        min_x = 30 + 105 * i
        max_x = 135 + 105 * i

        if y_coord in range(this_coord_tup[0], card_bottom) and x_coord in range(min_x, max_x):
            if not cs.do_move(i):
                illegal_move(min_x, card_bottom + 30)


def illegal_move(x_loc, y_loc):
    """Print ILLEGAL MOVE in bold red font at x_loc, y_loc."""

    illegal_text = tk.Text(root, bg="forest green", font=(
        "Courier", 20, "bold"), highlightthickness=0,
        fg="red", width=8, height=2)
    illegal_text.place(x=x_loc, y=y_loc)
    illegal_text.insert("1.0", "ILLEGAL\nMOVE")

    root.update()
    # Make the text go away after half a second
    root.after(500, illegal_text.destroy())


def place_poop():
    """Place a poop image at a random location on the screen, without
    allowing the image to go off the edge of the window. 
    """

    try:
        poop = tk.PhotoImage(file="GUI_Images/poop-emoji.gif").subsample(6)
    except FileNotFoundError:
        print("Not able to find the poop image, sorry. Good memes.")
        quit(1)

    width = poop.width()
    height = poop.height()

    poop_label = tk.Label(root, width=width, height=height, image=poop)
    # Need to anchor poop to poop_label so that Garbage Collection
    # doesn't make it go away
    poop_label.photo = poop

    poop_label.place(x=random.randrange(800 - width),
                     y=random.randrange(800 - height))


def cool_effect(title_text, index, str):
    """Prints a string str on tkinter label that text T is on, by
    printing a letter in str then waiting 80 milliseconds.
    """

    # THIS METHOD WAS TAKEN FROM STACK OVERFLOW by TigerhawkT3: 
    # https://stackoverflow.com/questions/37059668/
    # typewriter-effect-in-tkinter

    title_text.insert(index, str[0])

    if len(str) > 1:

        # Find index of next char
        index = title_text.index(f"{index} + 1 char")

        # Display the next character after 80 milliseconds
        title_text.after(80, cool_effect, title_text, index, str[1:])


def welcome_screen():
    """Display the welcome screen with a welcome message and a button
    to start the game.
    """

    # Learned how to center text from Stack Overflow:
    # https://stackoverflow.com/questions/42560585/
    # how-do-i-center-text-in-the-tkinter-text-widget

    title_text = tk.Text(root, bg="forest green",
                         font=("Courier", 30), pady=100)
    title_text.tag_configure("center", justify="center")

    cool_effect(title_text, "1.0", "Welcome to Cribbage Solitaire.")

    play_button = tk.Button(
        root, text="Start Game", highlightbackground="forest green",
        width=100, height=30, command=cs.play)
    play_button.place(x=350, y=250, width=100, height=30)

    title_text.tag_add("center", "1.0", "end")
    title_text.place(x=0, y=0, width=800)


if __name__ == '__main__':
    cs = CribbageSolitaireGUI()

    root = tk.Tk()
    root.geometry('800x800')
    root.configure(bg="forest green")

    root.bind('<Key>', key_handler)
    root.bind('<Button-1>', click_handler)
    root.update()

    # Give the user a second to get ready before starting
    root.after(1000, welcome_screen())
    root.mainloop()
