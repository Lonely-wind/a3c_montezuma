# -*- coding: utf-8 -*-
import tensorflow as tf
import numpy as np
import random

from game_state import GameState
from game_ac_network import GameACSimpleNetwork
from a3c_training_thread import A3CTrainingThread
from rmsprop_applier import RMSPropApplier

from constants import ACTION_SIZE
from constants import PARALLEL_SIZE
from constants import CHECKPOINT_DIR
from constants import RMSP_EPSILON
from constants import RMSP_ALPHA
from constants import GRAD_NORM_CLIP
from constants import USE_GPU

import time
import sys, select, termios, tty

settings = termios.tcgetattr(sys.stdin)

action_name = ['DOWN', 'UP', 'LEFT', 'RIGHT']

def getKey():
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [])
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key


def choose_action(pi_values):
  return np.random.choice(range(len(pi_values)), p=pi_values)  

def choose_max_action(pi_values):
  ans = pi_values[0] - 1
  k = -1
  for i in range(len(pi_values)):
    if pi_values[i] > ans:
      k = i
      ans = pi_values[i]
  return k

# use CPU for display tool
device = "/cpu:0"

global_network = GameACSimpleNetwork(ACTION_SIZE, -1, device)

sess = tf.Session()
init = tf.global_variables_initializer()
sess.run(init)

saver = tf.train.Saver()
checkpoint = tf.train.get_checkpoint_state(CHECKPOINT_DIR)
if checkpoint and checkpoint.model_checkpoint_path:
  saver.restore(sess, checkpoint.model_checkpoint_path)
  print("checkpoint loaded:", checkpoint.model_checkpoint_path)
else:
  print("Could not find old checkpoint")

game_state = GameState(0,display=True)

while True:
    key = getKey()
    if key == 'x':
        exit()
    elif key == 'n': # new game
        game_state.reset()
        continue
    elif key == 'a': # take an action
    
      pi_values = global_network.run_policy(sess, game_state.s_t)
      
      action = choose_action(pi_values)
      print 'Action =', action_name[action]
      game_state.process(action)

      if game_state.terminal:
        print '@@ Game terminate!'
        game_state.reset()
      else:
        game_state.update()


print 'evaluation done.'