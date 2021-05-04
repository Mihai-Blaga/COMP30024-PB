"""
Utility file containing all important components for choosing an action.
"""

import m.util
import m.update
import random

#Weights for Factors
attacker_proximity = 0  #weight for sum of closest attackers, prefer large
target_proximity = 0    #weight for sum of closest targets, prefer small
aggression = -5         #weight for closest target, prefer small
shyness = 0            #weight for closest attacker, prefer large
p_p_l = 1
e_p_l = 1
p_n_v_p = 1
e_n_v_p = 1
p_p_i = 1
e_p_i = 1
p_t_s = 1
e_t_s = 1
t_c = 1

no_to_piece = {0: "r", 1: "p", 2: "s"}
piece_to_no = {"r": 0, "p": 1, "s": 2}

DEBUG = False #set to TRUE if you want output for code in action.

def log(*args):
    if DEBUG:
        print(*args)


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

    #Start Calculating values
    player_pieces_left = throws_left + len(state[player])
    enemy_pieces_left = throws_left + len(state[opponent])

    player_num_vulnerable_pieces = 0
    player_temp_safe = [0,0,0]
    player_piece_invul = [0,0,0]

    enemy_num_vulnerable_pieces = 0
    enemy_temp_safe = [0,0,0]
    enemy_piece_invul = [0,0,0]

    sum_to_attackers = 0
    sum_to_targets = 0
    
    #Yep
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

        if closest_attacker == 1:
            player_num_vulnerable_pieces = player_num_vulnerable_pieces + 1
        elif closest_attacker == 10:
            player_temp_safe[piece_to_no[piece[0]]] = 1
            if opponent_throws_left == 0:
                player_piece_invul[piece_to_no[piece[0]]] = 1

        sum_to_attackers = sum_to_attackers + closest_attacker
        sum_to_targets = sum_to_targets + closest_target

        closest_of_all_attackers = min(closest_of_all_attackers, closest_attacker)
        closest_of_all_targets = min(closest_of_all_targets, closest_target)

    
    for piece in state[opponent]:
        closest_attacker = 10
        closest_target = 10

        attacker = no_to_piece[(piece_to_no[piece[0]] + 1) % 3]
        target = no_to_piece[(piece_to_no[piece[0]] - 1) % 3]

        if (piece[1] < player_upper and piece[1] > player_lower):
            closest_target = 1
        else:
            for a in pieces[opponent][attacker]:
                dist = m.util.calc_dist(a[0],a[1],piece[1],piece[2])
                closest_attacker = min(closest_attacker, dist)
        
        if closest_attacker == 1:
            enemy_num_vulnerable_pieces = enemy_num_vulnerable_pieces + 1
        elif closest_attacker == 10:
            enemy_temp_safe[piece_to_no[piece[0]]] = 1
            if throws_left == 0:
                enemy_piece_invul[piece_to_no[piece[0]]] = 1

    #sum_to_targets = sum_to_targets + closest_target
    closest_of_all_targets = min(closest_of_all_targets, closest_target)

    #scoring function
    score = sum_to_attackers*attacker_proximity
    score = score + closest_of_all_attackers*shyness
    score = score + sum_to_targets*target_proximity
    score = score + closest_of_all_targets*aggression
    score = score + p_p_l*player_pieces_left
    score = score + e_p_l * enemy_pieces_left
    score = score + p_n_v_p * player_num_vulnerable_pieces
    score = score + e_n_v_p * enemy_num_vulnerable_pieces
    score = score + p_p_i * sum(player_piece_invul)
    score = score + e_p_i * sum(enemy_piece_invul)
    score = score + p_t_s * sum(player_temp_safe)
    score = score + e_t_s * sum(enemy_temp_safe)
    score = score + t_c * throws_left

    log(state)
    log(sum_to_attackers*attacker_proximity,closest_of_all_attackers*shyness,sum_to_targets*target_proximity,closest_of_all_targets*aggression,p_p_l*player_pieces_left,e_p_l * enemy_pieces_left,p_n_v_p * player_num_vulnerable_pieces,e_n_v_p * enemy_num_vulnerable_pieces,p_p_i * sum(player_piece_invul),e_p_i * sum(enemy_piece_invul),p_t_s * sum(player_temp_safe),e_t_s * sum(enemy_temp_safe),t_c * throws_left)
    log(score)

    return score

def make_greedy_move(moves, state, player):
    max_score = -9999999
    greedy_move = ()
    best_moves = []
    throw_conversion = {-1:"r", -2:"p", -3:"s"}

    for key in moves:
        possible = moves[key]
        for hex in possible:
            """
            opponent = m.util.calculate_opponent(player)
            #pick throw token based on closest opposing player
            if (key == -1 and len(state[opponent]) != 0):
                min_dist = 10
                for piece in state[opponent]:
                    dist = m.util.calc_dist(hex[0], hex[1], piece[1], piece[2])
                    if (dist < min_dist):
                        throw_token = no_to_piece[(piece_to_no[piece[0]] + 1) % 3]
                        min_dist = dist
            """
            if (key < 0):
                move = output_move(key, throw_conversion[key], hex)
            else:
                move = output_move(key, (state[player][key][1], state[player][key][2]), hex)
            
            #evaluate what would happen if this move is made
            evaluating_state = m.update.update_board(state, move, player)
            evaluating_state = m.update.resolve_collisions(evaluating_state, hex)
            score = evaluate(evaluating_state, player)
            if max_score == -9999999:
                max_score = score
            #keep best move
            if (score == max_score):
                best_moves.append(move)
            elif (score > max_score):
                best_moves = [move]
                max_score = score
            
    greedy_move = random.choice(best_moves)

    return greedy_move

def make_random_move(moves, state, player):
    #makes a random choice of which piece to move and a random choice of where to move it.
    throw_conversion = {-1:"r", -2:"p", -3:"s"}

    key = random.choice(list(moves.keys()))
    hex = random.choice(moves[key])

    if (key < 0):
        move = output_move(key, throw_conversion[key], hex)
    else:   
        move = output_move(key, (state[player][key][1], state[player][key][2]), hex)

    return move

def output_move(piece, orig, final):
    if (piece < 0):
        return ("THROW", orig, final)
    
    if (m.util.calc_dist(orig[0], orig[1], final[0], final[1]) == 1):
        return ("SLIDE", orig, final)
    return ("SWING", orig, final)

