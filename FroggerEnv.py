# -*- coding: utf-8 -*-
"""
Created on Sun Mar 13 18:13:02 2022

@author: hannart1
"""

from io import StringIO
import numpy as np
import pygame
import time

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
    - n_actions: the number of actions the agent can take
    - n_tiles: the number of possible positions the agent can occupy
    - n_game_states: the number of possible game states (agent + environment)
    - frog_map: a 2D array containing unique position IDs [0:n_tiles-1]
    - frog_y: the current row position of the agent
    - frog_x: the current column position of the agent
    
    ### Methods
    - step(dir): returns the tuple (state, reward, game_stop)
        {dir -> is an integer value as described before...}
    - reset(): restarts the environment
    
    ### Version History
    * v0: Initial versions release (1.0.0)
    * v1: drank wine, added pygame visualation  (1.1.0)
    * v1: added more parameters to help with Q-table initialization (1.2.0)
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
        self.n_actions = 5
        self.n_tiles = self.n_col*self.n_row
        self.n_game_states = self.n_map_states*self.n_tiles
        self.frog_map= np.arange(self.n_tiles).reshape(self.n_row,self.n_col)
        self.frog_y = self.n_row-1
        self.frog_x = np.int(np.round(11*np.random.rand()))
        
        
        self.WIDTH = 20
        self.HEIGHT = 20
        self.MARGIN = 5
        self.C_CAR = (255,0,0)
        self.C_FROG = (0,255,0)
        self.C_NONE = (0,0,0)
        self.C_WIN = (255,255,255)
        self.C_COLLISION = (255,255,0)
        self.INITIALIZED = False

        
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
        
    def init_pygame_window(self):
        pygame.init()
        window_size = [300, 150]
        self.scr = pygame.display.set_mode(window_size)
        pygame.display.set_caption("Frogger")
        self.INITIALIZED = True
        
    def display_env(self, style):
        """
        Displays the current state of the environment (agent included) in plain
        text in the output window. Eventually we should use the pygame
        library for a richer visualization.
        
        Parameters
        ----------
        style - 'text': displays using plain text
                'pygame': displays using pygame window

        Returns
        -------
        None
        """
        if style == 'text':
            outline = StringIO()
            current_map = self.map.copy()
            temp = list(current_map[self.frog_y])
            temp[self.frog_x] = '@'
            current_map[self.frog_y] = ''.join(temp)       
            for rr in range(self.n_row):    
                outline.write(current_map[rr][0:self.n_col] + '\n')
            print(outline.getvalue())
            
        if style == 'pygame':
            if self.INITIALIZED==False:
                self.init_pygame_window()
                
            for rr in range(self.n_row):
                for cc in range(self.n_col):
                    color = (255, 0, 0)
                    if self.map[rr][cc] == 'C':
                        pygame.draw.rect(self.scr,
                             self.C_CAR,
                             [(self.MARGIN + self.WIDTH) * cc + self.MARGIN,
                              (self.MARGIN + self.HEIGHT) * rr + self.MARGIN,
                              self.WIDTH,
                              self.HEIGHT])
                    if self.map[rr][cc] == 'N' or self.map[rr][cc] =='F':
                        pygame.draw.rect(self.scr,
                             self.C_NONE,
                             [(self.MARGIN + self.WIDTH) * cc + self.MARGIN,
                              (self.MARGIN + self.HEIGHT) * rr + self.MARGIN,
                              self.WIDTH,
                              self.HEIGHT])
            if self.map[self.frog_y][self.frog_x] == 'N':
                color = self.C_FROG
            if self.map[self.frog_y][self.frog_x] == 'F':
                color = self.C_WIN
            if self.map[self.frog_y][self.frog_x] == 'C':
                color = self.C_COLLISION
            pygame.draw.rect(self.scr,
                 color,
                 [(self.MARGIN + self.WIDTH) * self.frog_x + self.MARGIN,
                  (self.MARGIN + self.HEIGHT) * self.frog_y + self.MARGIN,
                  self.WIDTH,
                  self.HEIGHT])
            pygame.display.update()
        
            
            
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
        self.display_env('pygame')
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
        
        
