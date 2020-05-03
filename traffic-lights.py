#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Traffic lights is an impartial abstract game invented by Alan Parr.

    It is played on a 3x4 board with a supply of red, yellow, and green markers.

    The object is to get a line of three of any color.

    On each turn, you must do ONE of the following:

     (1) Put a green counter in an empty square.
     (2) Replace a green counter with a yellow one.
     (3) Replace a yellow counter with a red one.

    So ultimately the board will fill with red counters.

"""

__all__      = ["traffic_lights"]
__author__   = "Carlos Luna-Mota"
__license__  = "The Unlicense"
__version__  = "20200503"

import random
import time

try: input = raw_input  # Use raw_input function for Python 2
except NameError: pass  # Use input     function for Python 3

try:              clock = time.clock         # Use clock function for Python 2
except NameError: clock = time.perf_counter  # Use perf_counter   for Python 3

### CONSTANTS (DO NOT CHANGE THEM!) ############################################

NAME     = tuple(letter + number for letter in "ABCD" for number in "1234")
INFINITY =  3**12
ILLEGAL  =  2
UNKNOWN  =  0
PREV     = -1
NEXT     =  1

### AUXILIARY FUNCTIONS ########################################################

def game_hash(board):
    """
    Returns a hash value representing the board such that:

        game_hash(B1) == game_hash(B2)  <=>  B1 is a rotation/reflection of B2

    """

    INDICES = ((0,1,2,3,4,5,6,7,8,9,10,11), (11,10,9,8,7,6,5,4,3,2,1,0),
               (8,9,10,11,4,5,6,7,0,1,2,3), (3,2,1,0,7,6,5,4,11,10,9,8))

    return min(sum(board[i]<<(e*2) for e,i in enumerate(I)) for I in INDICES)

def game_moves(board):
    """
    Returns the list of all legal moves available from the current position.

    Moves are represented directly as the resulting game positions.

    If the game is over, it returns an empty list.

    """

    LINES = ((0,1,2),(1,2,3),(4,5,6),(5,6,7),(8,9,10),(9,10,11),(0,4,8),
             (1,5,9),(2,6,10),(3,7,11),(0,5,10),(1,6,11),(2,5,8),(3,6,9))

    # If the game is over: return an empty list
    if any(0 < board[x] == board[y] == board[z] for x,y,z in LINES): return []

    # Otherwise: compute and return a list with all the legal moves
    moves = []
    for i in range(12):
        if board[i] < 3:
            moves.append(tuple(b+1 if i==j else b for j,b in enumerate(board)))
    return moves

def game_value(board, depth, cache):
    """
    A simple recursive negamax solver for Traffic Lights.

    Returns who wons in the current position:

        value = PREV        if the player that just played wons
        value = NEXT        if the player that plays next wons
        value = UNKNOWN     if it is unknown due to AI limitations

    """

    # Check if we already know the value of this position:
    h = game_hash(board)
    if h in cache: return cache[h]

    # Otherwise compute the game value of this position:
    else:

        # If the game is over, the previous player has won.
        moves = game_moves(board)
        if not moves: value = PREV

        # If we run out of depth, the value is UNKNOWN
        elif depth == 0: value = UNKNOWN

        # Otherwise, the value depends on the best move the adversary can do:
        else:
            value = PREV
            for move in moves:
                value = max(value, -game_value(move, depth-1, cache))
                if value == NEXT: break

        # Remember and return the value of this position:
        if value != UNKNOWN: cache[h] = value
        return value

def geneate_AIs(computer, human, preload_info):
    """Initializes the computer and the human AI assistants."""

    # Initialize the AIs:
    computer_AI = dict()
    human_AI    = dict()

    # Pre-load additional information:
    if preload_info:
        print("\n Loading...\n")
        timer = time.clock()
        BOARD = tuple(0 for _ in range(12))
        if human < computer:
            value = game_value(BOARD, human, human_AI)
            computer_AI.update(human_AI)
            value = game_value(BOARD, computer, computer_AI)
        else:
            value = game_value(BOARD, computer, computer_AI)
            human_AI.update(computer_AI)
            value = game_value(BOARD, human, human_AI)
        print(" Game loaded in {:.3f} seconds\n".format(time.clock()-timer))
        print("\n " + "═"*33 + "\n")

    # Add basic information:
    computer_AI["player"] = "computer"
    computer_AI["depth"]  = computer
    human_AI["player"]    = "human"
    human_AI["depth"]     = human

    # Return the AIs:
    return computer_AI, human_AI

def show(board, values):
    """Prints the board state and the AI analysis on the screen."""

    B  = (" 0 "," 1 "," 2 "," 3 ")
    V  = (" ? "," L ","   "," W ")
    R1 = [B[i] for i in board[0: 4]] + [V[i] for i in values[0: 4]]
    R2 = [B[i] for i in board[4: 8]] + [V[i] for i in values[4: 8]]
    R3 = [B[i] for i in board[8:12]] + [V[i] for i in values[8:12]]
    print("\n ┌─────────────────────┐                     ")
    print(  " │     1   2   3   4   │       AI analysis   ")
    print(  " │   ╔═══╤═══╤═══╤═══╗ │    ┌───┬───┬───┬───┐")
    print(  " │ A ║{:}│{:}│{:}│{:}║ │    │{:}│{:}│{:}│{:}│".format(*R1))
    print(  " │   ╟───┼───┼───┼───╢ │    ├───┼───┼───┼───┤")
    print(  " │ B ║{:}│{:}│{:}│{:}║ │    │{:}│{:}│{:}│{:}│".format(*R2))
    print(  " │   ╟───┼───┼───┼───╢ │    ├───┼───┼───┼───┤")
    print(  " │ C ║{:}│{:}│{:}│{:}║ │    │{:}│{:}│{:}│{:}│".format(*R3))
    print(  " │   ╚═══╧═══╧═══╧═══╝ │    └───┴───┴───┴───┘")
    print(  " └─────────────────────┘                     ")

def move(board, AI):
    """Returns a legal move made by the computer AI or the human."""

    # Compute and classify all legal moves:
    W, U, L, moves, values = [], [], [], {"X":None}, [ILLEGAL]*12
    for move in game_moves(board):
        cell         = [i for i in range(12) if board[i] != move[i]][0]
        name         = NAME[cell]
        moves[name]  = move
        values[cell] = game_value(move, AI["depth"], AI)
        if   values[cell] == PREV: W.append(name)
        elif values[cell] == NEXT: L.append(name)
        else:                      U.append(name)

    # Report results:
    show(board, values)

    # The computer chooses a legal move:
    if AI["player"] == "computer":
        if   W: move = random.choice(W)
        elif U: move = random.choice(U)
        elif L: move = random.choice(L)
        else:   move = "X"
        print("\n Computer move: " + move)

    # The player chooses a legal move:
    else:
        move = ""
        while move not in moves:
            try: move = input("\n What is your next move?\n\n > ").upper()[:2]
            except: pass

    # Return the board position resulting from this move:
    return moves[move]

### MAIN FUNCTION ##############################################################

def traffic_lights(computer, human):
    """
    A simple Human vs Computer command line implementation of Traffic Lights.

     * Parameter `computer` (integer >= 0) is the computer AI depth.
     * Parameter `human`    (integer >= 0) is the human-assistant AI depth.

    Use the `INFINITY` constant to get omniscient AIs. Use `0` to disable them.

    """

    assert(computer >= 0)
    assert(human    >= 0)

    # Preload some information into the AIs:
    computer_AI, human_AI = geneate_AIs(computer, human, preload_info=True)

    # Playing the game:
    while True:

        # Who plays first?
        turn = "X"
        while not turn in "HhCc":
            try: turn = input("\n Who plays first? (Human/Computer)\n\n > ")[0]
            except: pass
        is_computer_turn = turn in "Cc"

        # Play a new game:
        board = [0]*12
        while True:

            # If the game is over, report the winner:
            if not game_moves(board):
                show(board, [ILLEGAL]*12)
                if is_computer_turn: print("\n You have won!\n")
                else:                print("\n You have lost!\n")
                print("\n " + "═"*33 + "\n")
                break

            # Otherwise, make a move:
            if is_computer_turn: board = move(board, computer_AI)
            else:                board = move(board, human_AI)
            is_computer_turn = not is_computer_turn

            # Something went wrong, reset the game:
            if board == None: break

        # Play again?
        play_again = "?"
        while not play_again in "YyNn":
            try: play_again = input("\n Play again? (Yes/No)\n\n > ")[0]
            except: pass
        if play_again in "Nn": break

if __name__ == "__main__": traffic_lights(computer=3, human=3)

################################################################################
