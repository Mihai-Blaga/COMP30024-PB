import m.util
import m.action
import m.update

class Player:
    player_type = "upper"
    opponent = "lower"
    board_state = {}

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

        print("Initial player chosen:" + self.player_type)

        return

    def action(self):
        """
        Called at the beginning of each turn. Based on the current state
        of the game, select an action to play this turn.
        """
        moves = m.util.legal_moves(self.board_state, self.player_type)
        print("Moves for player: " + self.player_type)
        print(moves)

        move = m.action.make_greedy_move(moves, self.board_state, self.player_type)
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

