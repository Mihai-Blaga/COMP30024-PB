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
throw_conversion = {-1:"r", -2:"p", -3:"s"}

DEPTH = 2
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

def make_best_move(moves, state, player, max = True):
    #Returns (best_move, score) where best_move is the best move found and score is its respective score
    MAX = 9999999
    if max:
        best_score = 0-MAX
    else:
        best_score = MAX

    chosen_move = ()
    best_moves = []

    for key in moves:
        possible = moves[key]
        for hex in possible:
            """
            opponent = m.util.calculate_opponent(player)
            #   picking throw token based on closest opposing player
            if (key == -1 and len(state[opponent]) != 0):
                min_dist = 10
                for piece in state[opponent]:
                    dist = m.util.calc_dist(hex[0], hex[1], piece[1], piece[2])
                    if (dist < min_dist):
                        throw_token = no_to_piece[(piece_to_no[piece[0]] + 1) % 3]
                        min_dist = dist
            """
            (move, score) = convert_and_score(state, player, hex, key)
            
            if (best_score == 0-MAX) or (best_score == MAX):
                best_score = score
            #keep best move
            if (score == best_score):
                best_moves.append(move)
            elif ((max and score > best_score) or (not max and score < best_score)):
                best_moves = [move]
                best_score = score
            
    chosen_move = random.choice(best_moves)

    return (chosen_move, best_score)

def convert(state, player, hex, key):
    #returns the move in proper format
    if (key < 0):
        return output_move(key, throw_conversion[key], hex)
    else:
        return output_move(key, (state[player][key][1], state[player][key][2]), hex)

def convert_and_score(state, player, hex, key):
    #returns the best move and also scores it (move, score)
    move = convert(state, player, hex, key)
    
    #evaluate what would happen if this move is made
    evaluating_state = m.update.update_board(state, move, player)
    evaluating_state = m.update.resolve_collisions(evaluating_state, hex)
    score = evaluate(evaluating_state, player)

    return (move, score)

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

def paranoid_min_max(state, player):
    return min_max(state, player, (-999999, 999999), DEPTH*2)
    ...

#TODO: test min_max further
def min_max(state, player, threshold, depth, max = True):
    """
    Recursive min_max algorithm. 
    Returns (NULL, 0) if branch is pruned and (move, score) otherwise.
    """
    MAX = 9999999
    if max:
        mover = player
        best_score = 0-MAX
    else:
        mover = m.util.calculate_opponent(player)
        best_score = MAX
    moves = m.util.legal_moves(state, mover)
    chosen_move = ()
    best_moves = []

    if (depth == 1):
        #depth 1 will always be a min tree
        for key in moves:
            possible = moves[key]
            for hex in possible:
                (move, score) = convert_and_score(state, mover, hex, key)
                
                if (score < best_score):
                    best_moves = [move]
                    best_score = score
                
                if (score == best_score):
                    best_moves.append(move)
                
                if (best_score < threshold[0]):
                    #branch has been pruned
                    return (None, 0-MAX)

    elif (depth > 1):
        for key in moves:
            possible = moves[key]
            for hex in possible:
                #make move and update board
                move = convert(state, mover, hex, key)
                evaluating_state = m.update.update_board(state, move, mover)
                if (evaluating_state == None):
                    print("Null state?")
                    print(moves)
                    print(possible)
                    print(state)
                    print(move)
                    print(mover)
                    print(depth)

                if (not max):
                    evaluating_state = m.update.resolve_collisions(evaluating_state, hex)

                if max:
                    (best_lower_move, score) = min_max(state, player, (best_score, threshold[1]), depth-1, not max)
                if not max:
                    (best_lower_move, score) = min_max(state, player, (threshold[0], best_score), depth-1, not max)

                #checking if branch is pruned
                if best_lower_move == None:
                    continue
                
                if (max and score > best_score):
                    best_score = score
                    best_moves = [move]
                elif (min and score < best_score):
                    best_score = score
                    best_moves = [move]
                elif (best_score == score):
                    best_moves.append(move)

                #check pruning conditions
                if (max and best_score > threshold[1]):
                    return (None, MAX)
                elif (not max and best_score < threshold[0]):
                    return (None, 0-MAX)
            
    chosen_move = random.choice(best_moves)
    return (chosen_move, best_score)

def output_move(piece, orig, final):
    if (piece < 0):
        return ("THROW", orig, final)
    
    if (m.util.calc_dist(orig[0], orig[1], final[0], final[1]) == 1):
        return ("SLIDE", orig, final)
    return ("SWING", orig, final)

