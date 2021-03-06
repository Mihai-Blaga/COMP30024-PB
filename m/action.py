"""
Utility file containing all important components for choosing an action.
"""

from m.gametheory import solve_game
import m.util
import m.update
import random
import numpy as np
import scipy as sp

no_to_piece = {0: "r", 1: "p", 2: "s"}
piece_to_no = {"r": 0, "p": 1, "s": 2}
throw_conversion = {-1:"r", -2:"p", -3:"s"}

DEPTH = 1.5
DEBUG = False #set to TRUE if you want output for code in action.
A = True

def log(*args):
    if DEBUG:
        print(*args)

def temp_evaluate(state, player):
    opponent = m.util.calculate_opponent(player)
    return len(state[player]) + state[player + "_throws"] - len(state[opponent])

def evaluate(state, player):
    """
    Given a board state and the player making a move, evaluates the current state of the board
    """
    #setup
    opponent = m.util.calculate_opponent(player)

    throws_left = state[player + "_throws"]
    enemy_throws_left = state[opponent + "_throws"]

    #setting throw boundaries
    player_upper = 4
    player_lower = -4
    opponent_upper = 4
    opponent_lower = -4

    #if (throws_left > 0):
    #    if (player == "lower"):
    #        player_upper = (player_upper - throws_left) + 1
    #    if (player == "upper"):
    #        player_lower = (player_lower + throws_left) - 1

    #if (enemy_throws_left > 0):
    #    if (opponent == "lower"):
    #        opponent_upper = (opponent_upper - enemy_throws_left) + 1
    #    if (opponent == "upper"):
    #        opponent_lower = (opponent_lower + enemy_throws_left) - 1
        

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
    closest_target = 10
    closest_attacker = 10

    for piece in state[player]:
        closest_target = 10
        closest_attacker = 10
        
        attacker = no_to_piece[(piece_to_no[piece[0]] + 1) % 3]
        target = no_to_piece[(piece_to_no[piece[0]] + 2) % 3]

        if (piece[1] > opponent_lower and piece[1] < opponent_upper):
            #piece is within throw range
            pass
            #closest_attacker = 1
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
            if enemy_throws_left == 0:
                player_piece_invul[piece_to_no[piece[0]]] = 1

        sum_to_attackers = sum_to_attackers + closest_attacker
        sum_to_targets = sum_to_targets + closest_target

        closest_of_all_attackers = min(closest_of_all_attackers, closest_attacker)
        closest_of_all_targets = min(closest_of_all_targets, closest_target)

    if closest_of_all_attackers == 10:
        closest_of_all_attackers = 0

    for piece in state[opponent]:
        closest_attacker = 10
        attacker = no_to_piece[(piece_to_no[piece[0]] + 1) % 3]

        for a in pieces[player][attacker]:
            dist = m.util.calc_dist(a[0],a[1],piece[1],piece[2])
            closest_attacker = min(closest_attacker, dist)

        if closest_attacker == 10:
            enemy_temp_safe[piece_to_no[piece[0]]] = 1

    if player_pieces_left == 0 and enemy_pieces_left == 0:
        score = 50
    elif player_pieces_left == 0:
        score = -1000
    elif enemy_pieces_left == 0:
        score = 1000
    
    elif enemy_pieces_left == 1 and sum(player_piece_invul) > 0:
        if sum(enemy_piece_invul) == 0:
            score = 1000
        else:
            score = 50
    elif sum(enemy_piece_invul) > 0:
        score = -1000
    else:
        score = 50 + 20*(player_pieces_left + throws_left - enemy_pieces_left  - enemy_throws_left) + 2*(9 - closest_of_all_targets) + 15*throws_left -5*(sum(enemy_temp_safe))
        if closest_of_all_attackers == 1:
            score = score - 5

    log(state)
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
        opponent = m.util.calculate_opponent(player)
        counts_player = [0,0,0]
        counts_enemy = [0,0,0]
        #count all pieces this player has
        for p in state[player]:
            counts_player[piece_to_no[p[0]]] = counts_player[piece_to_no[p[0]]] + 1
        
        for p in state[opponent]:
            counts_enemy[piece_to_no[p[0]]] = counts_enemy[piece_to_no[p[0]]] + 1

        #randomly choose counter with fewest pieces
        best = []
        diff = 10
        
        i = 0
        while i < 3:
            temp_diff = counts_player[i] - counts_enemy[(i+2)%3]
            if temp_diff == diff:
                best.append(i)
            elif temp_diff < diff:
                diff = temp_diff
                best = [i]
            i = i + 1
        
        return output_move(key, no_to_piece[random.choice(best)], hex)
    else:
        return output_move(key, (state[player][key][1], state[player][key][2]), hex)

def convert_and_score(state, player, hex, key, scorer = 0):
    #returns the best move and also scores it (move, score)
    move = convert(state, player, hex, key)

    if (scorer == 0):
        scorer = player
    
    #evaluate what would happen if this move is made
    evaluating_state = m.update.update_board(state, move, player)
    evaluating_state = m.update.resolve_collisions(evaluating_state, hex)
    score = evaluate(evaluating_state, scorer)

    return (move, score)

def make_random_move(moves, state, player):
    #makes a random choice of which piece to move and a random choice of where to move it.
    throw_conversion = {-1:"r", -2:"p", -3:"s"}

    key = random.choice(list(moves.keys()))
    hex = random.choice(moves[key])

    piece_id = random.randrange(3) - 3

    if (key < 0):
        move = output_move(key, throw_conversion[piece_id], hex)
    else:   
        move = output_move(key, (state[player][key][1], state[player][key][2]), hex)

    return move

def paranoid_min_max(state, player, d = DEPTH):
    return serialised_min_max(state, player, (-9999999, 9999999), d*2, mx = True, aggressive = A)

def optimistic_min_max(state, player, d = DEPTH):
    return serialised_min_max(state, player, (-9999999, 9999999), d*2, mx = False, aggressive = A)

def serialised_min_max(state, player, threshold, depth, mx = True, aggressive = False):
    """
    Recursive min_max algorithm under serialised assumption.
    """
    MAX = 9999999
    alpha = threshold[0]
    beta = threshold[1]
    if mx:
        mover = player
        moves = m.util.legal_moves(state, mover, aggressive = aggressive)
        best_score = 0-MAX
    else:
        mover = m.util.calculate_opponent(player)
        moves = m.util.legal_moves(state, mover, aggressive = aggressive)
        best_score = MAX
        
    #keys = reversed(moves.keys())
    keys = moves.keys()

    chosen_move = ()
    best_moves = []

    log("DEPTH: ", depth, ", thresholds: ", (alpha, beta), ", max:", mx)
    
    if (depth == 1):
        for key in keys:
            possible = moves[key]
            for hex in possible:
                #make move and evaluate score relative to player
                (move, score) = convert_and_score(state, mover, hex, key, scorer = player)
                
                if (not mx and score < best_score):
                    best_moves = [move]
                    best_score = score
                    beta = min(beta, best_score)
                    log("score improved: ", best_score)

                elif (mx and score > best_score):
                    best_moves = [move]
                    best_score = score
                    alpha = max(alpha, best_score)
                    log("score improved: ", best_score)

                elif (score == best_score):
                    best_moves.append(move)
                    log("score equalled: ", best_score)
                
                if (beta <= alpha):
                    log("branch being pruned, ", best_score)
                    break
                    
    elif (depth > 0):
        for key in keys:
            possible = moves[key]
            for hex in possible:

                #make move and update board
                move = convert(state, mover, hex, key)
                evaluating_state = m.update.update_board(state, move, mover)
                if not mx:
                    evaluating_state = m.update.resolve_collisions(evaluating_state, hex)

                (next_move, score) = serialised_min_max(evaluating_state, player, (alpha, beta), depth-1, mx = not mx, aggressive= aggressive)

                if (mx and score > best_score):
                    best_score = score 
                    best_moves = [move]
                    alpha = max(alpha, best_score)
                    #log("score improved: ", best_score)

                elif (not mx and score < best_score):
                    best_score = score
                    best_moves = [next_move]
                    beta = min(beta, best_score)
                    #log("score improved: ", best_score)

                elif (best_score == score):
                    if mx:
                        best_moves.append(move)
                    else:    
                        best_moves.append(next_move)
                    #log("score equalled: ", best_score)

                #check pruning conditions
                if (beta <= alpha):
                    #log("branch being pruned, ", best_score)
                    break
    
    if (depth == 1):
        log(best_moves)

    chosen_move = random.choice(best_moves)
    return (chosen_move, best_score)

def populate_score_table(state, player):
    #returns table of scores where row = player move, col = opponent move
    opponent = m.util.calculate_opponent(player)
    upper_moves = m.util.legal_moves(state, player, aggressive=A)
    lower_moves = m.util.legal_moves(state, opponent)

    move_to_cols = {}
    move_to_rows = {}
    i = 0
    j = 0

    w = 0
    h = 0

    for k in upper_moves.keys():
        h = h + len(upper_moves[k])

    for k in lower_moves.keys():
        w = w + len(lower_moves[k])

    score_table = [[0 for x in range(w)] for y in range(h)]
    cols_to_move = [() for x in range(w)]
    rows_to_move = [() for x in range(h)]

    for uKey in upper_moves.keys():
        for uVal in upper_moves[uKey]:
            
            move_to_rows[uKey, uVal[0], uVal[1]] = i
            rows_to_move[i] = (uKey, uVal)
            j = 0
            u_move = convert(state, "upper", uVal, uKey)

            for lKey in lower_moves.keys():
                for lVal in lower_moves[lKey]:
                    
                    if i == 0:
                        move_to_cols[lKey, lVal[0], lVal[1]] = j
                        cols_to_move[j] = (lKey, lVal)

                    l_move = convert(state, "lower", lVal, lKey)
                    new_board = m.update.update_board(state, l_move, "lower")
                    new_board = m.update.update_board(new_board, u_move, "upper")
                    score = evaluate(new_board, player)

                    (score_table[i])[j] = score
                    j = j + 1
            i = i+1

    return (score_table, cols_to_move, rows_to_move)

def gm_output(state, player):
    #Attempt to build on top of the work done by Matthew Farrugia-Roberts
    (V, col_d, row_d) = populate_score_table(state, player)
    V = np.array(V)
    (prob_dist, sec_level) = solve_game(V)
    prob_dist = prob_dist.tolist()
    rnd = np.random.choice(len(prob_dist), 1, prob_dist)
    move = row_d[rnd[0]]

    print(state, player, move[0], move[1])

    return convert(state, player, move[1], move[0])

def get_optimistic_move(score_table):
    score_table = np.matrix(score_table)
    ax = 1
    
    scores = score_table.max(ax)

    return scores

def get_pessimistic_move(score_table):
    score_table = np.matrix(score_table)
    ax = 1
    
    scores = score_table.min(ax)

    return scores

def random_from_pessimistic(state, player):
    (table, col_d, row_d) = populate_score_table(state, player)
    scores = get_pessimistic_move(table).tolist()
    scores = [x for sublist in scores for x in sublist]
    mn = min(scores)

    sum = 0
    for i in range(len(scores)):
        scores[i] = scores[i] - mn + 1
        sum = sum + scores[i]

    for i in range(len(scores)):
        scores[i] = scores[i]/sum


    log(scores)
    rnd = np.random.choice(len(scores), 1, scores)
    move = row_d[rnd[0]]

    log(state, player, move[0], move[1])

    return convert(state, player, move[1], move[0])


def opt_pess_bounds(state, player):
    (table, cols_d, rows_d) = populate_score_table(state, player)
    best = np.amax(table)
    worst = np.amin(table)
    return (best, worst)

def populate_o_p_table(state, player):
    opponent = m.util.calculate_opponent(player)
    upper_moves = m.util.legal_moves(state, player, aggressive = A)
    lower_moves = m.util.legal_moves(state, opponent)

    i = 0
    j = 0

    w = 0
    h = 0

    for k in upper_moves.keys():
        h = h + len(upper_moves[k])

    for k in lower_moves.keys():
        w = w + len(lower_moves[k])

    opt_table = [[0 for x in range(w)] for y in range(h)]
    pess_table = [[0 for x in range(w)] for y in range(h)]

    (table, col_d, row_d) = populate_score_table(state, player)
    opt = get_optimistic_move(table)
    pess = get_pessimistic_move(table)
    
    min_pess = -99999999
    corr_opt = -99999999

    for (o, p) in zip(opt, pess):
        if min_pess < p:
            min_pess = p
            corr_opt = o

    for uKey in upper_moves.keys():
        for uVal in upper_moves[uKey]:
            if opt[i] >= corr_opt:
                j = 0
                u_move = convert(state, "upper", uVal, uKey)

                for lKey in lower_moves.keys():
                    for lVal in lower_moves[lKey]:

                        l_move = convert(state, "lower", lVal, lKey)
                        new_board = m.update.update_board(state, l_move, "lower")
                        new_board = m.update.update_board(new_board, u_move, "upper")
                        (o, p) = opt_pess_bounds(new_board, player)

                        (opt_table[i])[j] = o
                        (pess_table[i])[j] = p
                        j = j + 1
            i = i+1

    return (opt_table, pess_table)


def output_move(piece, orig, final):
    if (piece < 0):
        return ("THROW", orig, final)
    
    if (m.util.calc_dist(orig[0], orig[1], final[0], final[1]) == 1):
        return ("SLIDE", orig, final)
    return ("SWING", orig, final)

