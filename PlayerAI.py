import numpy as np
import random
import time
import Utils as utils
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
        self.lvl_weight = {0: 12, 1: 10, 2: 8, 3: 6, 4: 4, 5: 2}

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
            move = self.get_move_max(grid_copy, curr_pos, depth)

            # # find all available moves
            # available_moves = grid.get_neighbors(self.pos, only_available=True)
            #
            # # make random move
            # new_pos = random.choice(available_moves) if available_moves else None

        return move


    def get_move_max(self, grid_copy, curr_pos, depth):
        if depth >= self.max_depth:
            return (None, self.move_utility(grid_copy, curr_pos))

        max_util = (None, -np.inf)

        avail_moves = grid_copy.get_neighbors(curr_pos, only_available=True)
        avail_moves.sort(avail_moves, key=self.move_h_ocls(grid_copy, avail_moves))

        for move in avail_moves:
            depth += 1
            grid_copy.move(self.player_num, move)
            curr_pos = move
            result = self.get_move_min(grid_copy, curr_pos, depth)

            if result[1] > max_util[1]:
                max_util = result


        return max_util

    def get_move_min(self, grid_copy, curr_pos, depth):
        if depth >= self.max_depth:
            return (None, self.move_utility(grid_copy, curr_pos))

        min_util = (None, np.inf)

        for trap in grid_copy.get_neighbors(curr_pos, only_available=True):
            depth += 1
            trap_land = utils.throw_trap(player=(3 - self.player_num), grid=grid_copy, intended_position=trap)
            grid_copy.trap(trap_land)
            result = self.get_move_max(grid_copy, curr_pos, depth)

            if result[1] < min_util[1]:
                min_util = result

        return min_util

    def move_h_ocls(self, grid_copy, avail_moves):
        utility_l = []
        for move in avail_moves:
            utility_l.append(len(grid_copy.get_neighbors(move, only_available=True)))
        return utility_l

    def move_utility(self, grid_copy, curr_pos):
        level = 0
        num_of_traps = 0
        utility = 0
        # Continue expanding scope until we've reached limits of the board
        while len(utils.get_neighbors_by_level(curr_pos, level)) > len(utils.get_neighbors_by_level(curr_pos, level+1)):
            ns = utils.get_neighbors_by_level(curr_pos, level)
            avail_cells = grid_copy.getAvailableCells()

            # Count number of traps at the current level
            for elem in ns:
                if elem not in avail_cells:
                    num_of_traps += 1

            utility -= -(self.lvl_weight[level] * num_of_traps)
            trapped = utils.check_if_trapped(ns, num_of_traps)

            if trapped:
                return -np.inf

            level += 1
            num_of_traps = 0

        return


    def getTrap(self, grid : Grid) -> tuple:
        """ 
        YOUR CODE GOES HERE

        The function should return a tuple of (x,y) coordinates to which the player *WANTS* to throw the trap.
        
        It should be the result of the ExpectiMinimax algorithm, maximizing over the Opponent's *Move* actions, 
        taking into account the probabilities of it landing in the positions you want. 
        
        Note that you are not required to account for the probabilities of it landing in a different cell.

        You may adjust the input variables as you wish (though it is not necessary). Output has to be (x,y) coordinates.
        
        """
        time_for_trap = time.time() + self.time_for_trap
        while time.time() < time_for_trap:
            # find opponent
            opponent = grid.find(3 - self.player_num)

            # find all available cells surrounding Opponent
            available_cells = grid.get_neighbors(opponent, only_available=True)

            # throw to one of the available cells randomly
            trap = random.choice(available_cells)

        return trap

    