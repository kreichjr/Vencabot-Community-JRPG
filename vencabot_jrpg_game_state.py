class GameState:
    def __init__(self):
        # Initiate the starting game state and variables
        # Boss Flags
        self.boss_one_defeated = False
        self.boss_two_defeated = False
        
        # Story Flags
        self.storyline_quest_one_completed = False
        
        # Game Ending Flags
        self.game_over = False
        self.game_completed = False

        # Time Keeping
        self.game_clock = 0
        self.game_tick_counter = 0


    # Functions to set flags for the game state
    def set_boss_one_defeated_flag(self):
        self.boss_one_defeated = True

    def set_boss_two_defeated_flag(self):
        self.boss_two_defeated = True

    def set_storyline_quest_one_flag(self):
        self.storyline_quest_one_completed = True

    def set_game_over_flag(self):
        self.game_over = True

    def set_game_completed_flag(self):
        self.game_completed = True

    # Functions to return the game state flags
    def is_game_over(self):
        return self.game_over

    def is_game_completed(self):
        return self.game_completed


    

    