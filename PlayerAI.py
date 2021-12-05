import numpy as np
import random
import time
import sys
import os 
from BaseAI import BaseAI
from Grid import Grid

# TO BE IMPLEMENTED
# 
class PlayerAI(BaseAI):

    def __init__(self) -> None:
        # You may choose to add attributes to your player - up to you!
        super().__init__()
        self.pos = None
        self.player_num = None
        self.move_time = 5
        self.time_for_move = 2.5
        self.time_for_trap = 2.5
        self.max_depth = 5
    
    def getPosition(self):
        return self.pos

    def setPosition(self, new_position):
        self.pos = new_position 

    def getPlayerNum(self):
        return self.player_num

    def setPlayerNum(self, num):
        self.player_num = num

    def getMove(self, grid: Grid) -> tuple:
        """ 
        YOUR CODE GOES HERE

        The function should return a tuple of (x,y) coordinates to which the player moves.

        It should be the result of the ExpectiMinimax algorithm, maximizing over the Opponent's *Trap* actions, 
        taking into account the probabilities of them landing in the positions you believe they'd throw to.

        Note that you are not required to account for the probabilities of it landing in a different cell.

        You may adjust the input variables as you wish (though it is not necessary). Output has to be (x,y) coordinates.
        
        """
        time_for_move = time.time() + self.time_for_move
        while time.time() < time_for_move:
            curr_pos = grid.find(self.player_num)
            grid_copy = grid.clone()
            depth = 0
            new_pos = self.get_move_max(grid_copy, curr_pos, depth)

            # # find all available moves
            # available_moves = grid.get_neighbors(self.pos, only_available=True)
            #
            # # make random move
            # new_pos = random.choice(available_moves) if available_moves else None

        return new_pos


    def get_move_max(self, grid_copy, curr_pos, depth):
        if depth >= self.max_depth:
            return (curr_pos, self.move_utility(grid_copy))

        max_util = (None, -np.inf)

        for child in grid_copy.get_neighbors(curr_pos, only_available=True):
            depth += 1
            grid_copy.move(self.player_num, child)
            curr_pos = child
            result = self.get_move_min(grid_copy, curr_pos, depth)

            if result[1] > max_util[1]:
                max_util = result


        return max_util

    def get_move_min(self, grid_copy, curr_pos, depth):
        if depth >= self.max_depth:
            return (None, self.move_utility(grid_copy))

        min_util = (None, np.inf)

        for child in grid_copy.get_neighbors(grid_copy.find(3 - self.player_num,), only_available=True):
            depth += 1
            grid_copy.trap(child)
            result = self.get_move_max(grid_copy, curr_pos, depth)

            if result[1] < min_util[1]:
                min_util = result

        return min_util

    def move_h_is(self, grid_copy, new_pos):
        return len(grid_copy.get_neighbors(new_pos, only_available=True))

    def move_utility(self, grid):
        pass


    def getTrap(self, grid : Grid) -> tuple:
        """ 
        YOUR CODE GOES HERE

        The function should return a tuple of (x,y) coordinates to which the player *WANTS* to throw the trap.
        
        It should be the result of the ExpectiMinimax algorithm, maximizing over the Opponent's *Move* actions, 
        taking into account the probabilities of it landing in the positions you want. 
        
        Note that you are not required to account for the probabilities of it landing in a different cell.

        You may adjust the input variables as you wish (though it is not necessary). Output has to be (x,y) coordinates.
        
        """
        pass
        

    