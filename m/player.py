import m.util
import m.action
import m.update
import numpy as np
import scipy as sp

class Player:
    player_type = "upper"
    opponent = "lower"
    board_state = {}

    DEBUG = False

    def __init__(self, player):
        """
        Called once at the beginning of a game to initialise this player.
        Set up an internal representation of the game state.

        The parameter player is the string "upper" (if the instance will
        play as Upper), or the string "lower" (if the instance will play
        as Lower).
        """
        #setting player and opponent state
        if (player == self.opponent):
            self.opponent = self.player_type
            self.player_type = player
        
        #Initialising an empty board
        self.board_state = m.util.parse_json(m.util.EMPTY_JSON_PATH)
        return

    def action(self):
        """
        Called at the beginning of each turn. Based on the current state
        of the game, select an action to play this turn.
        """
        MAX = 9999999
        moves = m.util.legal_moves(self.board_state, self.player_type)
        if self.DEBUG:
            print("Moves for player: " + self.player_type)
            print(moves)

        (table, col_d, row_d) = m.action.populate_score_table(self.board_state, self.player_type)
        (opt_table, pess_table) = m.action.populate_o_p_table(self.board_state, self.player_type)
        
        print("opt: ", opt_table)
        print("pess: ", pess_table)
        '''
        optimistic = m.action.get_optimistic_move(table)
        pessimistic = m.action.get_pessimistic_move(table)

        print("optimistic: ", optimistic, col_d)
        print("pessimistic: ", pessimistic, col_d)
        '''

        (move, score) = m.action.optimistic_min_max(self.board_state, self.player_type)
        (move2, score2) = m.action.paranoid_min_max(self.board_state, self.player_type)
        #print("Optimistic: ", move, ", score: ", score)
        #print("Pessimistic: ", move2, ", score: ", score2)
        #(move, score) = m.action.min_max(self.board_state, self.player_type, (0-MAX, MAX), 2)
        if self.DEBUG:
            print("Making move: ", move)
        return move


    def update(self, opponent_action, player_action):
        """
        Called at the end of each turn to inform this player of both
        players' chosen actions. Update your internal representation
        of the game state.
        The parameter opponent_action is the opponent's chosen action,
        and player_action is this instance's latest chosen action.
        """
        self.board_state = m.update.update_board(self.board_state, opponent_action, self.opponent)
        self.board_state = m.update.update_board(self.board_state, player_action, self.player_type)

        self.board_state = m.update.resolve_collisions(self.board_state, opponent_action[2])
        self.board_state = m.update.resolve_collisions(self.board_state, player_action[2])

