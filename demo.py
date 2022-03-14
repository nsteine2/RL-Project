# -*- coding: utf-8 -*-
"""
Created on Mon Mar 14 01:31:03 2022

@author: hannart1
"""

import numpy as np
import time
import FroggerEnv

env = FroggerEnv.FroggerEnv()
# Q-table initialization
Q = np.zeros([env.n_game_states,env.n_actions])


while True:
    state, reward, stop = env.step(np.round(4*np.random.rand()))
    print(state, reward, stop)
    time.sleep(0.5)