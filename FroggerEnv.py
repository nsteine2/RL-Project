# -*- coding: utf-8 -*-
"""
Created on Sun Mar 13 18:13:02 2022

@author: hannart1
"""

from io import StringIO
import numpy as np

class FroggerEnv():
    """
    Frogger involves trying to sucessfully move the agent (froggy) across the street
    while avoiding getting hit by moving cars. [Later we talked about adding in
    floating logs and river obstacles, but for now keeping it simple.]
    
    The agent takes a 1-element vector for actions.
    The action space is `(dir)`, where `dir` decides direction to move in which can be:
    - 0: NONE
    - 1: LEFT
    - 2: RIGHT
    - 3: UP
    - 4: DOWN
    
    ### Observation Space
    The observation is a value representing the agent's current position as
    a unique identifier based on the number of available positions on the map
    n_row * n_col. Since the environment is also changing, the game state is modified 
    by the current state of the map:
        current_state = [current_row][n_col] + [current_col] + map_state*[n_row][n_col]
        
    ### Rewards
    Reward schedule:
    - Reach finish(F): 50
    - Reach car(H): -20
    - Reach empty(F): -1
    
    ### Parameters
    - map: the current environement (agent not included)
    - map_state: the current map state identifier
    - n_map_states: the number of possible map states (periodic environment)
    - n_col: the number of horizontal tiles
    - n_row: the number of vertical tiles
    - n_tiles: the number of possible positions the agent can occupy
    - frog_map: a 2D array containing unique position IDs [0:n_tiles-1]
    - frog_y: the current row position of the agent
    - frog_x: the current column position of the agent
    
    ### Methods
    - step(dir): returns the tuple (state, reward, game_stop)
        {dir -> is an integer value as described before...}
    - reset(): restarts the environment
    
    ### Version History
    * v0: Initial versions release (1.0.0)
    """


    def __init__(self):
        """ 
        Class constructor
        Currently, takes no input arguments.
        """
        self.map = ['FFFFFFFFFFFFFFFFFFFFFFFF',
                    'CCCCCCNNNNNNCCCCCCNNNNNN',
                    'NNNCCCNNNNNNNNNCCCNNNNNN',
                    'NCCCCCNNNNNNNCCCCCNNNNNN',
                    'NNNNNNNCCNNNNNNNNNNCCNNN',
                    'NNNNNNNNNNNNNNNNNNNNNNNN'
                    ]
        self.map_state = 0
        self.n_map_states = 24
        self.n_col = 12
        self.n_row = 6
        self.n_tiles = self.n_col*self.n_row
        self.frog_map= np.arange(self.n_tiles).reshape(self.n_row,self.n_col)
        self.frog_y = self.n_row-1
        self.frog_x = np.int(np.round(11*np.random.rand()))
        
    def update_car_map(self):
        """
        Updates the list of strings which represent the position of the cars 
        within the environment. Currently, the car lengths and speeds are hard
        coded in. We may want to change this to make it more flexible if we 
        want to explore other traffic configurations easily.
        
        Returns
        -------
        None
        """
        self.map[1] = self.map[1][-1] + self.map[1][0:-1]
        self.map[2] = self.map[2][2:] + self.map[2][0:2]
        if(np.mod(self.map_state,2) == 0):
            self.map[3] = self.map[3][-1] + self.map[3][0:-1]
        self.map[4] = self.map[4][1:] + self.map[4][0]
        
    def display_env(self):
        """
        Displays the current state of the environment (agent included) in plain
        text in the output window. Eventually we should use the pygame
        library for a richer visualization.
        
        Returns
        -------
        None
        """
        outline = StringIO()
        current_map = self.map.copy()
        temp = list(current_map[self.frog_y])
        temp[self.frog_x] = '@'
        current_map[self.frog_y] = ''.join(temp)       
        for rr in range(self.n_row):    
            outline.write(current_map[rr][0:self.n_col] + '\n')
        print(outline.getvalue())
    
    def update_frog_position(self,action):
        '''
        This updates the position of the froggy based on the input action 
        command. Currently, the agent is not permitted to travel beyond the 
        edges of the environment (there's no 'wrap-around').

        Parameters
        ----------
        action : integer indicating direction
            0: none
            1: left
            2: right
            3: up
            4: down

        Returns
        -------
        None.

        '''
        if action==0:
            pass
        if action==1:
            if self.frog_x==0:
                pass
            else:
                self.frog_x -= 1
        if action==2:
            if self.frog_x==self.n_col-1:
                pass
            else:
                self.frog_x += 1
        if action==3:
            if self.frog_y==0:
                pass
            else:
                self.frog_y -= 1
        if action==4:
            if self.frog_y==self.n_row-1:
                pass
            else:
                self.frog_y += 1
                
    def calculate_rewards(self):
        """
        Calculates the rewards for the last action. Looks up the value of the 
        map at the current agent position, returns values based on the 
        character value.

        Returns
        -------
        reward - reward for last action
        stop_game - boolean indicating whether stop condition is met
        """
        current_tile = self.map[self.frog_y][self.frog_x]
        if current_tile=='N':
            reward = -1
            stop_game = False
        if current_tile=='C':
            reward = -20
            stop_game = True
        if current_tile=='F':
            reward = 50
            stop_game = True
        return reward, stop_game
    
    def calculate_game_state(self):
        """
        Calcuates the current game state, which depends on both the agent's
        position, as well as the current map_state.

        Returns
        -------
        state : a unqiue ID denoting the current state of the game.

        """
        position_id = self.frog_map[self.frog_y][self.frog_x]
        state = position_id + self.map_state*self.n_tiles
        return state
                
    def step(self, action):
        """
        

        Parameters
        ----------
        action : integer indicating direction
            0: none
            1: left
            2: right
            3: up
            4: down

        Returns
        -------
        state : a unique ID denoting the current state of the game
        reward : reward for the last action
        stop_game : boolean indicating whether stop conidition is met

        """
        self.update_car_map()
        self.update_frog_position(action)
        self.display_env()
        self.map_state = np.mod(self.map_state+1, self.n_map_states)
        state = self.calculate_game_state()
        reward, stop_game = self.calculate_rewards()
        return state, reward, stop_game
        
    def reset(self):
        """
        Resets the environment and agent.

        Returns
        -------
        None.

        """
        self.__init__()
        