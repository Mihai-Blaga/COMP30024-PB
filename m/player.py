import m.util

class Player:
    def __init__(self, player):
        """
        Called once at the beginning of a game to initialise this player.
        Set up an internal representation of the game state.

        The parameter player is the string "upper" (if the instance will
        play as Upper), or the string "lower" (if the instance will play
        as Lower).
        """
        #setting player state
        if (player == "lower"):
            m.util.upper_player = False
        
        #Initialising an empty board
        data = m.util.parse_json(m.util.EMPTY_JSON_PATH)
        board_state = m.util.parse_board(data)

        print("Initial player chosen:")
        m.util.check_upper()

        return

    def action(self):
        """
        Called at the beginning of each turn. Based on the current state
        of the game, select an action to play this turn.
        """
        # put your code here
    
    def update(self, opponent_action, player_action):
        """
        Called at the end of each turn to inform this player of both
        players' chosen actions. Update your internal representation
        of the game state.
        The parameter opponent_action is the opponent's chosen action,
        and player_action is this instance's latest chosen action.
        """
        # put your code here

