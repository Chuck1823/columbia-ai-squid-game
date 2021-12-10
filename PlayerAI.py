import numpy as np
import random
import time
import Utils as utils

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
        self.lvl_weight = {0: 50, 1: 40, 2: 30, 3: 20, 4: 10, 5: 2}
        self.man_dist_conversion = {0: 8, 1: 7, 2: 6, 3: 5, 4: 4, 5: 3}
        self.grid_copy = None

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
        curr_pos = grid.find(self.player_num)
        depth = 0
        self.grid_copy = grid.clone()
        move = self.get_move_max(self.grid_copy, curr_pos, depth, time_for_move)

        return move[0]


    def get_move_max(self, grid_copy, curr_pos, depth, time_for_move):
        if depth >= self.max_depth or (time.time() > time_for_move):
            return (None, self.move_utility(grid_copy, curr_pos))

        max_util = (None, -np.inf)
        depth += 1

        avail_moves = grid_copy.get_neighbors(curr_pos, only_available=True)

        # move_h_ocls(grid_copy, avail_moves), move_h_is(grid_copy, avail_moves), move_h_aisgrid_copy, avail_moves),
        # move_h_manhattan_dist_to_middle(avail_moves) as available heuristics
        avail_moves.sort(key=self.move_h_ocls, reverse=True)

        for move in avail_moves:
            grid_copy = grid_copy.move(move, self.player_num)
            curr_pos = move
            result = self.get_move_min(grid_copy, curr_pos, depth, time_for_move)

            if result[1] > max_util[1]:
                max_util = (curr_pos, result[1])


        return max_util

    def get_move_min(self, grid_copy, curr_pos, depth, time_for_move):
        if depth >= self.max_depth or (time.time() > time_for_move):
            return (None, self.move_utility(grid_copy, curr_pos))

        min_util = (None, np.inf)
        depth += 1

        for trap in grid_copy.get_neighbors(curr_pos, only_available=True):
            trap_land = utils.grid_copy_throw_trap(grid_copy.find(3 - self.player_num), grid_copy, trap)
            grid_copy = grid_copy.trap(trap_land)
            result = self.get_move_max(grid_copy, curr_pos, depth, time_for_move)

            if result[1] < min_util[1]:
                min_util = (curr_pos, result[1])

        return min_util

    def move_h_ocls(self, move):
        return len(self.grid_copy.get_neighbors(move, only_available=True))

    def move_h_is(self, move):
        return len(self.grid_copy.get_neighbors(move, only_available=True) - len(self.grid_copy.get_neighbors(self.grid_copy.find((3 - self.player_num)), only_available=True)))

    def move_h_ais(self, move):
        return len(self.grid_copy.get_neighbors(move, only_available=True) - (2 * len(self.grid_copy.get_neighbors(self.grid_copy.find((3 - self.player_num)), only_available=True))))

    def move_h_manhattan_dist_to_middle(self, avail_moves):
        utility_l = []
        for move in avail_moves:
            manhattan_dist = np.abs(move[0], -3) + np.abs(move[1], -3)
            if manhattan_dist > 5:
                utility_l.append(3)
            else:
                utility_l.append(self.man_dist_conversion[manhattan_dist])

        return utility_l

    def move_utility(self, grid_copy, curr_pos):
        level = 0
        num_of_traps = 0
        utility = 0
        avail_cells = grid_copy.getAvailableCells()
        # Iteratively identifies the neighboring cells of a player that have traps, level by level with a continued
        # expansion of the scope until we've reached limits of the board. Assigns each level some weight based on
        # proximity of traps to the player. Meanwhile, it checks if the player is trapped which would cause imminent
        # loss from the player

        # There can only be max 3 levels to explore
        while level < 4:
            ns = utils.get_neighbors_by_level(curr_pos, level)

            # Count number of traps at the current level
            for elem in ns:
                if elem not in avail_cells:
                    num_of_traps += 1

            utility += -(self.lvl_weight[level] * num_of_traps)
            trapped = utils.check_if_trapped(ns, num_of_traps)

            if trapped:
                return -np.inf

            level += 1
            num_of_traps = 0

        return utility


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

    