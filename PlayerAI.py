import numpy as np
import random
import time
import sys
import os

from numpy.lib import utils 
from BaseAI import BaseAI
from Grid import Grid
from Utils import manhattan_distance

# TO BE IMPLEMENTED
# 
class PlayerAI(BaseAI):

    def __init__(self) -> None:
        # You may choose to add attributes to your player - up to you!
        super().__init__()
        self.pos = None
        self.player_num = None
        self.oppo_num = None
        self.time_for_trap = 2.5
        self.move_time = 5
        self.max_depth = 5
    
    def getPosition(self):
        return self.pos

    def setPosition(self, new_position):
        self.pos = new_position 

    def getPlayerNum(self):
        return self.player_num

    def setPlayerNum(self, num):
        self.player_num = num
        self.oppo_num = 3 - num

    def getMove(self, grid: Grid) -> tuple:
        """ 
        YOUR CODE GOES HERE

        The function should return a tuple of (x,y) coordinates to which the player moves.

        It should be the result of the ExpectiMinimax algorithm, maximizing over the Opponent's *Trap* actions, 
        taking into account the probabilities of them landing in the positions you believe they'd throw to.

        Note that you are not required to account for the probabilities of it landing in a different cell.

        You may adjust the input variables as you wish (though it is not necessary). Output has to be (x,y) coordinates.
        
        """
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
        time_limit = time.time() + self.time_for_trap
        oppo_pos = grid.find(self.oppo_num)
        depth = 0
        trap = self.get_trap_max(grid,oppo_pos,depth, time_limit)
        if not trap[0]:
            return random.choice(grid.get_neighbors(oppo_pos))
        return trap[0]


    def get_trap_chance(self, grid, oppo_pos, trap_pos, depth, time_limit):
        #probability
        p = 1 - 0.05*(manhattan_distance(trap_pos,self.pos)-1)
        result = 0
        poss_trap = grid.get_neighbors(trap_pos)
        if oppo_pos in poss_trap:
            poss_trap.remove(oppo_pos)
        miss_p = (1-p)/len(poss_trap)
        if miss_p > 0.05:
            for neighbor in poss_trap:
                grid_copy = grid.clone()
                grid_copy.trap(neighbor)
                result += miss_p* self.get_trap_min(grid, oppo_pos, depth, time_limit)
        grid_copy = grid.clone()
        grid_copy.trap(trap_pos)
        result += p*self.get_trap_min(grid, oppo_pos, depth, time_limit)
        return result

    def get_trap_max(self,grid, oppo_pos, depth, time_limit):
        if depth >= self.max_depth or time.time()>= time_limit:
            return (None, self.trap_utility(grid,oppo_pos))
        max_util = (None, -np.inf)
        avail_trap = grid.get_neighbors(oppo_pos, only_available = True)
        depth += 1

        for trap in avail_trap:
            result = self.get_trap_chance(grid, oppo_pos, trap, depth, time_limit)
            if result[1] > max_util[1]:
                max_util = result

        return max_util
        

    def get_trap_min(self,grid, oppo_pos, depth, time_limit):
        if depth >= self.max_depth or time.time() >= time_limit:
            return (None, self.trap_utility(grid,oppo_pos))
        min_util = (None, np.inf)
        depth += 1

        for move in grid.get_neighbors(oppo_pos, only_available = True):
            grid.move(move, self.oppo_num)
            result = self.get_trap_max(grid, oppo_pos, depth)
            
            if result[1] < min_util[1]:
                min_util = (move, result[1])

        return min_util

    
    def trap_utility(self,grid, oppo_pos):
        #IS
        player_moves = grid.get_neighbors(self.pos,only_available = True)
        oppo_moves = grid.get_neighbors(oppo_pos,only_available = True)
        utility = len(player_moves)-len(oppo_moves)
        return utility
    
    