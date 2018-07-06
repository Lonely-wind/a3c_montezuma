# -*- coding: utf-8 -*-
import sys
import numpy as np

from toy_Montezuma import ACTION_SIZE
from tm_wrapper import MontezumaWrapper as Wrapper, FEATURE_SIZE
HISTORY = 2
STATE_SIZE = FEATURE_SIZE * HISTORY

class GameState(object):
  def __init__(self, rand_seed=113, display=False, no_op_max=7):

    self.game = Wrapper(display=display)
    self.reset()

  def _process_frame(self, action):
    reward = self.game.act(action)
    terminal = self.game.game_over()

    self._feature = self.game.get_feature()
    
    return reward, terminal, self._feature

  def reset(self):
    self.game.reset_game()
    
    x_t = self.game.get_feature()
    self._feature = x_t
    
    self.reward = 0
    self.terminal = self.game.game_over()
    #self.s_t = x_t
    self.s_t = np.concatenate((x_t, x_t))
    
  def process(self, action, state_count):
    
    r, t, x_t1 = self._process_frame(action)

    self.terminal = t
    #self.s_t1 = x_t1
    self.s_t1 = np.concatenate((self.s_t[FEATURE_SIZE:], x_t1))  

    self.s_t1.flags.writeable = False
    state_count[self.s_t1.data] += 1
    # print 'Dict Size:', len(state_count)
    intrinsic_reward = 0.01 / np.sqrt(state_count[self.s_t1.data])

    self.reward = r + intrinsic_reward

  def update(self):
    self.s_t = self.s_t1
