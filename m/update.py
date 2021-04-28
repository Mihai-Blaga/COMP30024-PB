"""
Utility file containing all important components for updating the board state.
"""
import m.util
import copy

def update_board(state, move, player):
    """
    Given a board state, a move and a player, updates the internal version of the board.
    """
    board_state = copy.deepcopy(state)
    move_type = move[0]
    before = move[1]
    after = move[2]

    if (move_type == "THROW"):
        board_state[player].append((before, after[0], after[1]))
        return board_state

    for i in range(0, len(board_state[player])):
        piece = board_state[player][i]
        if (piece[1] == before[0] and piece[2] == before[1]):
            board_state[player][i] = (piece[0], after[0], after[1])
            return board_state

def resolve_collisions(state, hex):
    """
    Resolving collisions based on the newest move performed
    """
    pieces_on_hex = []

    #looks at all pieces which are on the new hex
    for piece in state["upper"] + state["lower"]:
        if (piece[1] == hex[0] and piece[2] == hex[1]):
            pieces_on_hex.append(piece[0])

    pieces_on_hex = list(set(pieces_on_hex))

    #removes the pieces which would not survive being on the hex
    for piece in state["upper"]:
        if (piece[1] == hex[0] and piece[2] == hex[1]):
            for tile in pieces_on_hex:
                if (not m.util.live_hex(hex[0], hex[1], piece[0], tile)):
                    state["upper"].remove(piece)

    for piece in state["lower"]:
        if (piece[1] == hex[0] and piece[2] == hex[1]):
            for tile in pieces_on_hex:
                if (not m.util.live_hex(hex[0], hex[1], piece[0], tile)):
                    state["lower"].remove(piece)