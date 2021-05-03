"""
Utility file containing a large portion of our own part A project code.
Functions crossed-over include: valid_hex, finished (modified), adj_hex, adj_loc, live_hex, calc_dist, dist_board.
"""
import json
import sys

#constants
EMPTY_JSON_PATH = "./m/empty.json"

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

def calculate_opponent(player):
    opponent = "lower"
    if player == "lower":
        opponent = "upper"
    return opponent

def finished(state):
    """
    For a given board state, confirms it is in an accepted "finished" state based on absence of any lower pieces.
    TODO: rest of the finishing conditions
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

def adj_loc(state, player):
    """
    Returns list of all potential moves for each moveable piece. Format {movable_piece_num: [moves]}
    """
    pieces = state[player]
    moves = {}

    for i in range(0, len(pieces)):
        hex_moves = []
        for j in range(0, len(pieces)):
            #Looking for swing moves (for piece one hex away)
            if (i != j and (calc_dist(pieces[i][1], pieces[i][2], pieces[j][1], pieces[j][2]) == 1)):
                swing_moves = adj_hex(pieces[j][1], pieces[j][2])
                hex_moves = hex_moves + swing_moves

        hex_moves = hex_moves + adj_hex(pieces[i][1], pieces[i][2])
        hex_moves = list(set(hex_moves)) #remove duplicates
        hex_moves = [x for x in hex_moves if x != (pieces[i][1], pieces[i][2])] #removing stationary moves

        moves[i] = hex_moves

    return moves

def legal_moves(state, player):
    """
    Returns a list of all legal moves including throws. Format {movable_piece_num: [moves]}
    A throw is given a movable_piece_num of -1.
    """
    print(state)
    legal_moves = adj_loc(state, player)
    throws_left = state[player + "_throws"]

    upper = 4
    lower = -4

    if (throws_left > 0):
        if (player == "lower"):
            upper = (upper - throws_left) + 1
        if (player == "upper"):
            lower = (lower + throws_left) - 1
    
    throws = []
    for i in range(lower, upper + 1):
        for j in range (-4, 5):
            if (valid_hex(i,j)):
                throws.append((i,j))
    
    legal_moves[-1] = throws
    return legal_moves

def live_hex(r, q, target_piece, original_piece):
    """
    returns true if the target piece will survive moving to the specified hex
    """
    #maps pieces from rock, paper, scissors or blank to a ordinal number for maths.
    piece_map = {'r': 0, 'P': 1, 's': 2, 'R': 3, 'p': 4, 'S': 5, '': -2}

    if (not (valid_hex(r,q))):
        return False

    original_piece = piece_map[original_piece]
    target_piece = piece_map[target_piece]

    if (original_piece != -2 and target_piece != -2):
        return not ((((original_piece + 1) % 6) == target_piece) or (((original_piece + 4) % 6) == target_piece))

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
    """
    loads in board state from a json file.
    """
    try:
        with open(file_path) as file:
            data = json.load(file)
    except IndexError:
        print("invlid json path", file=sys.stderr)
        sys.exit(1)
    
    return data