"""
Utility file containing a large portion of part A project code.
COMP30024 Artificial Intelligence, Semester 1, 2021
Project Part A: Searching

This module contains some helper functions for printing actions and boards.
Feel free to use and/or modify them to help you develop your program.
"""
import json
import sys
import m.player

#constants
upper_player = True
board_state = {}
considered_moves = {}
EMPTY_JSON_PATH = "./m/empty.json"

def check_upper():
    if upper_player:
        print("Upper")
    else:
        print("Lower")
    return

def valid_hex(r, q):
    """
    For any hexagon (r,q) returns True if it would 
    appear on a standard 5-sided hexagonal board.
    """
    if (r > 4 or r < -4 or q > 4 or q < -4):
        return False
    minimum_val = max(-4, -4-q)
    maximum_val = min(4, 4-q)
    return ((minimum_val <= r) and (maximum_val >= r))

def finished(state):
    """
    For a given board state, confirms it is in an accepted "finished" state based on absence of any lower pieces.
    """
    return ((len(state["lower"]) == 0 and state["lower_throws"] == 0) or \
        (len(state["upper"]) == 0 and state["upper_throws"] == 0)) 

def adj_hex(r1, q1):
    """
    Returns list of all adjacent hexes to target hex
    """
    hexes = []
    if (valid_hex(r1 - 1, q1)):
        hexes.append((r1 - 1, q1))
    if (valid_hex(r1 + 1, q1)):
        hexes.append((r1 + 1, q1))
    if (valid_hex(r1, q1 - 1)):
        hexes.append((r1, q1 - 1))
    if (valid_hex(r1, q1 + 1)):
        hexes.append((r1, q1 + 1))
    if (valid_hex(r1 - 1, q1 + 1)):
        hexes.append((r1 - 1, q1 + 1))
    if (valid_hex(r1 + 1, q1 - 1)):
        hexes.append((r1 + 1, q1 - 1))

    return hexes

def live_hex(r, q, target_piece, original_piece):
    """
    returns true if the target piece will survive moving to the specified hex
    """
    #maps pieces from rock, paper, scissors or blank to a ordinal number for maths.
    piece_map = {'r': 0, 'P': 1, 's': 2, 'R': 3, 'p': 4, 'S': 5, '': -2}

    if (target_piece == '#' or not (valid_hex(r,q))):
        return False

    original_piece = piece_map[original_piece]
    target_piece = piece_map[target_piece]

    if (original_piece != -2 and target_piece != -2):
        return not (((original_piece + 1) % 6) == target_piece or ((original_piece + 4) % 6) == target_piece)

    return True

def calc_dist(r1, q1, r2, q2):
    """
    Returns distance between hexes (r1, q1) and (r2, q2)
    """

    if((not valid_hex(r1, q1)) or (not valid_hex(r2, q2))):
        return -1
    
    dist = max(abs(r1-r2), abs(q1-q2), abs((r1+q1) - (r2+q2)))

    return dist

def dist_board(r, q):
    """
    Outputs a dictionary of the form {(r, q): distance from target hex}
    """
    if (not valid_hex(r, q)):
        return -1

    dist_dict = {}

    for i in range(-4, 5):
        for j in range(-4, 5):
            if (valid_hex(i, j)):
                dist_dict[(i, j)] = calc_dist(i, j, r, q)

    return dist_dict

def parse_json(file_path):
    try:
        with open(file_path) as file:
            data = json.load(file)
    except IndexError:
        print("invlid json path", file=sys.stderr)
        sys.exit(1)
    
    return data

def parse_board(data):
    """
    DEBUGGING FUNCTION
    Outputs a dictionary of the form (r, q): piece-code.
    """
    board_dict = {}

    upper = data["upper"]
    lower = data["lower"]

    for i in range(-4, 5):
        for j in range(-4, 5):
            if (valid_hex(i, j)):
                board_dict[(i, j)] = ''

    for piece in upper:
        board_dict[(piece[1], piece[2])] = piece[0].upper()

    for piece in lower:
        board_dict[(piece[1], piece[2])] = piece[0]

    return board_dict

def print_board(board_dict, message="", compact=True, ansi=False, **kwargs):
    """
    For help with visualisation and debugging: output a board diagram with
    any information you like (tokens, heuristic values, distances, etc.).

    Arguments:

    board_dict -- A dictionary with (r, q) tuples as keys (following axial
        coordinate system from specification) and printable objects (e.g.
        strings, numbers) as values.
        This function will arrange these printable values on a hex grid
        and output the result.
        Note: At most the first 5 characters will be printed from the string
        representation of each value.
    message -- A printable object (e.g. string, number) that will be placed
        above the board in the visualisation. Default is "" (no message).
    ansi -- True if you want to use ANSI control codes to enrich the output.
        Compatible with terminals supporting ANSI control codes. Default
        False.
    compact -- True if you want to use a compact board visualisation,
        False to use a bigger one including axial coordinates along with
        the printable information in each hex. Default True (small board).
    
    Any other keyword arguments are passed through to the print function.

    Example:

        >>> board_dict = {
        ...     ( 0, 0): "hello",
        ...     ( 0, 2): "world",
        ...     ( 3,-2): "(p)",
        ...     ( 2,-1): "(S)",
        ...     (-4, 0): "(R)",
        ... }
        >>> print_board(board_dict, "message goes here", ansi=False)
        # message goes here
        #              .-'-._.-'-._.-'-._.-'-._.-'-.
        #             |     |     |     |     |     |
        #           .-'-._.-'-._.-'-._.-'-._.-'-._.-'-.
        #          |     |     | (p) |     |     |     |
        #        .-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-.
        #       |     |     |     | (S) |     |     |     |
        #     .-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-.
        #    |     |     |     |     |     |     |     |     |
        #  .-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-.
        # |     |     |     |     |hello|     |world|     |     |
        # '-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'
        #    |     |     |     |     |     |     |     |     |
        #    '-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'
        #       |     |     |     |     |     |     |     |
        #       '-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'
        #          |     |     |     |     |     |     |
        #          '-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'
        #             | (R) |     |     |     |     |
        #             '-._.-'-._.-'-._.-'-._.-'-._.-'
    """
    if compact:
        template = """# {00:}
#              .-'-._.-'-._.-'-._.-'-._.-'-.
#             |{57:}|{58:}|{59:}|{60:}|{61:}|
#           .-'-._.-'-._.-'-._.-'-._.-'-._.-'-.
#          |{51:}|{52:}|{53:}|{54:}|{55:}|{56:}|
#        .-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-.
#       |{44:}|{45:}|{46:}|{47:}|{48:}|{49:}|{50:}|
#     .-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-.
#    |{36:}|{37:}|{38:}|{39:}|{40:}|{41:}|{42:}|{43:}|
#  .-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-.
# |{27:}|{28:}|{29:}|{30:}|{31:}|{32:}|{33:}|{34:}|{35:}|
# '-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'
#    |{19:}|{20:}|{21:}|{22:}|{23:}|{24:}|{25:}|{26:}|
#    '-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'
#       |{12:}|{13:}|{14:}|{15:}|{16:}|{17:}|{18:}|
#       '-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'
#          |{06:}|{07:}|{08:}|{09:}|{10:}|{11:}|
#          '-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'
#             |{01:}|{02:}|{03:}|{04:}|{05:}|
#             '-._.-'-._.-'-._.-'-._.-'-._.-'"""
    else:
        template = """# {00:}
#                  ,-' `-._,-' `-._,-' `-._,-' `-._,-' `-.
#                 | {57:} | {58:} | {59:} | {60:} | {61:} |
#                 |  4,-4 |  4,-3 |  4,-2 |  4,-1 |  4, 0 |
#              ,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-.
#             | {51:} | {52:} | {53:} | {54:} | {55:} | {56:} |
#             |  3,-4 |  3,-3 |  3,-2 |  3,-1 |  3, 0 |  3, 1 |
#          ,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-.
#         | {44:} | {45:} | {46:} | {47:} | {48:} | {49:} | {50:} |
#         |  2,-4 |  2,-3 |  2,-2 |  2,-1 |  2, 0 |  2, 1 |  2, 2 |
#      ,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-.
#     | {36:} | {37:} | {38:} | {39:} | {40:} | {41:} | {42:} | {43:} |
#     |  1,-4 |  1,-3 |  1,-2 |  1,-1 |  1, 0 |  1, 1 |  1, 2 |  1, 3 |
#  ,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-.
# | {27:} | {28:} | {29:} | {30:} | {31:} | {32:} | {33:} | {34:} | {35:} |
# |  0,-4 |  0,-3 |  0,-2 |  0,-1 |  0, 0 |  0, 1 |  0, 2 |  0, 3 |  0, 4 |
#  `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-'
#     | {19:} | {20:} | {21:} | {22:} | {23:} | {24:} | {25:} | {26:} |
#     | -1,-3 | -1,-2 | -1,-1 | -1, 0 | -1, 1 | -1, 2 | -1, 3 | -1, 4 |
#      `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-'
#         | {12:} | {13:} | {14:} | {15:} | {16:} | {17:} | {18:} |
#         | -2,-2 | -2,-1 | -2, 0 | -2, 1 | -2, 2 | -2, 3 | -2, 4 |
#          `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-'
#             | {06:} | {07:} | {08:} | {09:} | {10:} | {11:} |
#             | -3,-1 | -3, 0 | -3, 1 | -3, 2 | -3, 3 | -3, 4 |   key:
#              `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-'     ,-' `-.
#                 | {01:} | {02:} | {03:} | {04:} | {05:} |       | input |
#                 | -4, 0 | -4, 1 | -4, 2 | -4, 3 | -4, 4 |       |  r, q |
#                  `-._,-' `-._,-' `-._,-' `-._,-' `-._,-'         `-._,-'"""
    # prepare the provided board contents as strings, formatted to size.
    ran = range(-4, +4+1)
    cells = []
    for rq in [(r,q) for r in ran for q in ran if -r-q in ran]:
        if rq in board_dict:
            cell = str(board_dict[rq]).center(5)
            if ansi:
                # put contents in bold
                cell = f"\033[1m{cell}\033[0m"
        else:
            cell = "     " # 5 spaces will fill a cell
        cells.append(cell)
    # prepare the message, formatted across multiple lines
    multiline_message = "\n# ".join(message.splitlines())
    # fill in the template to create the board drawing, then print!
    board = template.format(multiline_message, *cells)
    print(board, **kwargs)