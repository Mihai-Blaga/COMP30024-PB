"""
Utility file containing all important components for choosing an action.
"""

import m.util
import m.update
import random

attacker_proximity = 1  #weight for sum of closest attackers, prefer large
target_proximity = 1    #weight for sum of closest targets, prefer small
aggression = 10         #weight for closest target, prefer small
shyness = 10            #weight for closest attacker, prefer large

no_to_piece = {0: "r", 1: "p", 2: "s"}
piece_to_no = {"r": 0, "p": 1, "s": 2}

def evaluate(state, player):
    """
    Given a board state and the player making a move, evaluates the current state of the board
    """
    #setup
    opponent = m.util.calculate_opponent(player)

    throws_left = state[player + "_throws"]
    opponent_throws_left = state[opponent + "_throws"]

    #setting throw boundaries
    player_upper = 4
    player_lower = -4
    opponent_upper = 4
    opponent_lower = -4

    if (throws_left > 0):
        if (player == "lower"):
            player_upper = (player_upper - throws_left) + 1
        if (player == "upper"):
            player_lower = (player_lower + throws_left) - 1

    if (opponent_throws_left > 0):
        if (opponent == "lower"):
            opponent_upper = (opponent_upper - opponent_throws_left) + 1
        if (opponent == "upper"):
            opponent_lower = (opponent_lower + opponent_throws_left) - 1
        

    #dictionary of dictionaries based on piece label
    pieces = {"upper": {"r": [], "p": [], "s": []}, "lower": {"r": [], "p": [], "s": []}}

    for piece in state["upper"]:
        pieces["upper"][piece[0]].append((piece[1], piece[2]))

    for piece in state["lower"]:
        pieces["lower"][piece[0]].append((piece[1], piece[2]))

    sum_to_attackers = 0
    sum_to_targets = 0
    closest_of_all_attackers = 10
    closest_of_all_targets = 10

    for piece in state[player]:
        closest_target = 10
        closest_attacker = 10
        
        attacker = no_to_piece[(piece_to_no[piece[0]] + 1) % 3]
        target = no_to_piece[(piece_to_no[piece[0]] - 1) % 3]

        if (piece[1] > opponent_lower and piece[1] < opponent_upper):
            #piece is within throw range
            closest_attacker = 1
        else:
            for a in pieces[opponent][attacker]:
                dist = m.util.calc_dist(a[0],a[1],piece[1],piece[2])
                closest_attacker = min(closest_attacker, dist)

        for t in pieces[opponent][target]:
            dist = m.util.calc_dist(t[0],t[1],piece[1],piece[2])
            closest_target = min(closest_target, dist)

        sum_to_attackers = sum_to_attackers + closest_attacker
        sum_to_targets = sum_to_targets + closest_target

        closest_of_all_attackers = min(closest_of_all_attackers, closest_attacker)
        closest_of_all_targets = min(closest_of_all_targets, closest_target)

    closest_target = 10
    for piece in state[opponent]:
        if (piece[1] < player_upper and piece[1] > player_lower):
            closest_target = 1

    sum_to_targets = sum_to_targets + closest_target
    closest_of_all_targets = min(closest_of_all_targets, closest_target)

    #scoring function
    score = sum_to_attackers*attacker_proximity
    score = score + closest_of_all_attackers*shyness
    score = score - sum_to_targets*target_proximity
    score = score - closest_of_all_targets*aggression

    return score

def make_greedy_move(moves, state, player):
    opponent = m.util.calculate_opponent(player)
    min_score = 9999999
    greedy_move = ()
    best_moves = []
    throw_token = "r"

    for key in moves:
        possible = moves[key]
        for hex in possible:
            #pick throw token based on closest opposing player
            if (key == -1 and len(state[opponent]) != 0):
                min_dist = 10
                for piece in state[opponent]:
                    dist = m.util.calc_dist(hex[0], hex[1], piece[1], piece[2])
                    if (dist < min_dist):
                        throw_token = no_to_piece[(piece_to_no[piece[0]] + 1) % 3]
                        min_dist = dist
            
            if (key == -1):
                move = output_move(key, throw_token, hex)
            else:
                move = output_move(key, (state[player][key][1], state[player][key][2]), hex)
            
            #evaluate what would happen if this move is made
            evaluating_state = m.update.update_board(state, move, player)
            evaluating_state = m.update.resolve_collisions(evaluating_state, hex)
            score = evaluate(evaluating_state, player)
            
            #keep best move
            if (score == min_score):
                best_moves.append(move)
            elif (score < min_score):
                best_moves = [move]
                min_score = score
            
    greedy_move = random.choice(best_moves)

    return greedy_move

def output_move(piece, orig, final):
    if piece == -1:
        return ("THROW", orig, final)
    
    if (m.util.calc_dist(orig[0], orig[1], final[0], final[1]) == 1):
        return ("SLIDE", orig, final)
    return ("SWING", orig, final)

