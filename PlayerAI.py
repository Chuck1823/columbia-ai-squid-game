import numpy as np
import random
import time
import Utils as utils

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
        time_for_move = time.time() + self.time_for_move
        curr_pos = grid.find(self.player_num)
        depth = 0
        alpha = -np.inf
        beta = np.inf
        self.grid_copy = grid.clone()
        move = self.get_move_max(self.grid_copy, curr_pos, depth, time_for_move, alpha, beta)
        if not move[0]:
            # find all available moves
            available_moves = grid.get_neighbors(self.pos, only_available=True)
            # make random move
            return random.choice(available_moves) if available_moves else None

        return move[0]


    def get_move_max(self, grid_copy, curr_pos, depth, time_for_move, alpha, beta):
        if depth >= self.max_depth or (time.time() > time_for_move):
            return (None, self.move_utility(grid_copy, curr_pos))

        max_util = (None, -np.inf)
        depth += 1

        avail_moves = grid_copy.get_neighbors(curr_pos, only_available=True)

        # move_h_ocls(grid_copy, avail_moves), move_h_is(grid_copy, avail_moves), move_h_aisgrid_copy, avail_moves),
        # move_h_manhattan_dist_to_middle(avail_moves) as available heuristics
        avail_moves.sort(key=self.move_h_ais, reverse=True)

        for move in avail_moves:
            grid_copy = grid_copy.move(move, self.player_num)
            curr_pos = move
            result = self.get_move_min(grid_copy, curr_pos, depth, time_for_move, alpha, beta)

            if result[1] > max_util[1]:
                max_util = (curr_pos, result[1])

            if max_util[1] >= beta:
                break

            if max_util[1] >= alpha:
                alpha = max_util[1]


        return max_util

    def get_move_min(self, grid_copy, curr_pos, depth, time_for_move, alpha, beta):
        if depth >= self.max_depth or (time.time() > time_for_move):
            return (None, self.move_utility(grid_copy, curr_pos))

        min_util = (None, np.inf)
        depth += 1

        for trap in grid_copy.get_neighbors(curr_pos, only_available=True):
            trap_land = utils.grid_copy_throw_trap(grid_copy.find(3 - self.player_num), grid_copy, trap)
            grid_copy = grid_copy.trap(trap_land)
            result = self.get_move_max(grid_copy, curr_pos, depth, time_for_move, alpha, beta)

            if result[1] < min_util[1]:
                min_util = (curr_pos, result[1])

            if min_util[1] <= alpha:
                break

            if min_util[1] < beta:
                beta = min_util[1]

        return min_util

    def move_h_ocls(self, move):
        return len(self.grid_copy.get_neighbors(move, only_available=True))

    def move_h_is(self, move):
        return len(self.grid_copy.get_neighbors(move, only_available=True)) - len(self.grid_copy.get_neighbors(self.grid_copy.find((3 - self.player_num)), only_available=True))

    def move_h_ais(self, move):
        return len(self.grid_copy.get_neighbors(move, only_available=True)) - (2 * len(self.grid_copy.get_neighbors(self.grid_copy.find((3 - self.player_num)), only_available=True)))

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
        time_limit = time.time() + self.time_for_trap
        oppo_pos = grid.find(self.oppo_num)
        depth = 0
        alpha = -np.inf
        beta = np.inf
        trap = self.get_trap_max(grid,oppo_pos,depth, time_limit, alpha, beta)
        #If minmax returns None due to either time out or No ceils available
        if not trap[0]:
            print("random select")
            return random.choice(grid.getAvailableCells())
        return trap[0]


    def get_trap_chance(self, grid, oppo_pos, trap_pos, depth, time_limit, alpha, beta):
        #probability
        p = 1 - 0.05*(manhattan_distance(trap_pos,self.pos)-1)
        result = 0
        poss_trap = grid.get_neighbors(trap_pos)
        if oppo_pos in poss_trap:
            poss_trap.remove(oppo_pos)
        miss_p = (1-p)/len(poss_trap)
        if miss_p > 0.1:
            for neighbor in poss_trap:
                grid_copy = grid.clone()
                grid_copy.trap(neighbor)
                result += miss_p * self.get_trap_min(grid_copy, oppo_pos, depth, time_limit, alpha, beta)[1]
        grid_copy = grid.clone()
        grid_copy.trap(trap_pos)
        result += p * self.get_trap_min(grid_copy, oppo_pos, depth, time_limit, alpha, beta)[1]
        return (trap_pos,result)

    def get_trap_max(self,grid, oppo_pos, depth, time_limit, alpha, beta):
        if depth >= self.max_depth or time.time()>= time_limit:
            return (None, self.trap_utility(grid,oppo_pos))
        max_util = (None, -np.inf)
        avail_trap = self.get_avail_trap(grid,oppo_pos)
        #avail_trap = grid.get_neighbors(oppo_pos, only_available = True)
        if len(avail_trap) == 0:
            return (None, np.inf)
        depth += 1
        avail_trap.sort(key = self.get_trap_h, reverse = True)
        for trap in avail_trap:
            result = self.get_trap_chance(grid, oppo_pos, trap, depth, time_limit, alpha, beta)
            if result[1] > max_util[1]:
                max_util = (trap,result[1])
            if time.time()>= time_limit:
                return max_util
            if max_util[1] >= beta:
                break
            if max_util[1] > alpha:
                alpha = max_util[1]
        return max_util
        
    def get_trap_min(self,grid, oppo_pos, depth, time_limit, alpha, beta):
        if depth >= self.max_depth or time.time() >= time_limit:
            return (None, self.trap_utility(grid,oppo_pos))
        min_util = (None, np.inf)
        depth += 1
        self.grid_copy = grid
        avail_move = grid.get_neighbors(oppo_pos, only_available = True)
        avail_move.sort(key = self.move_h_ocls,reverse = True)
        for move in avail_move:
            grid.move(move, self.oppo_num)
            result = self.get_trap_max(grid, oppo_pos, depth, time_limit, alpha, beta)
            
            if result[1] < min_util[1]:
                min_util = (move, result[1])
            if time.time() >= time_limit:
                return min_util
            if min_util[1] <= alpha:
                break
            if min_util[1] < beta:
                beta = min_util[1]
        return min_util

    def get_trap_h(self,trap):
        return len(self.grid_copy.get_neighbors(trap,only_available=True))
    def trap_utility_IS(self,grid, oppo_pos):
        #IS
        player_moves = grid.get_neighbors(self.pos,only_available = True)
        oppo_moves = grid.get_neighbors(oppo_pos,only_available = True)
        utility = len(player_moves)-len(oppo_moves)
        #
        return utility
    
    def trap_utility(self,grid, oppo_pos):
        #combine IS and Lookahead
        #The available moves one step ahead is weighted based on current avaiable moves
        player_moves = grid.get_neighbors(self.pos,only_available = True)
        oppo_moves = grid.get_neighbors(oppo_pos,only_available = True)
        num_move = 0
        utility = len(player_moves)-len(oppo_moves)
        for move in player_moves:
            num_move += len(grid.get_neighbors(move,only_available = True))
        utility += num_move/(len(player_moves)+1)
        num_move = 0    
        for move in oppo_moves:
            num_move += len(grid.get_neighbors(move,only_available = True))
        utility -= num_move/(len(oppo_moves)+1)
        return utility

    def get_avail_trap(self,grid,pos):

        """
        Description
        -----------
        The function returns the neighboring cells of a certain cell in the board, given its x,y coordinates

        Parameters
        -----------
        pos : position (x,y) whose neighbors are desired

        only_available (bool) : if True, the function will return only available neighboring cells. 
                                default = False
        
        """
        x,y = pos
        
        valid_range = lambda t: range(max(t-2, 0), min(t+3, grid.dim))

        # find all neighbors
        neighbors = list({(a,b) for a in valid_range(x) for b in valid_range(y)} - {(x,y)})
        return [neighbor for neighbor in neighbors if grid.map[neighbor] == 0]
    