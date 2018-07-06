from __future__ import print_function
import numpy as np
from game_state import GameState, STATE_SIZE, ACTION_SIZE
from collections import namedtuple
import random
import copy
from queue import Queue, PriorityQueue, LifoQueue
import gym

Unit = namedtuple('Unit', ('state', 'action','reward'))

class trajectory_collection(object):
	def __init__(self, capacity=100):
		self.capacity = capacity
		self.memory = []
		self.current_tj = []
		self.m_idx = 0
		self.c_idx = 0

	def done(self):
		if len(self.memory) < self.capacity:
			self.memory.append(None)
		self.memory[self.m_idx] = self.current_tj # need deepcopy?
		self.current_tj = []
		self.m_idx = (self.m_idx + 1) % self.capacity

	def add_unit(self, *args):
		self.current_tj.append(Unit(*args))

	def print_one(self, i):
		print(self.memory[i])

	def print_last_action_seq(self):
		x = self.memory[(self.m_idx+self.capacity-1)%self.capacity]
		for y in x:
			print(y.action, end='')
		print()

	def print_last(self):
		print(self.memory[(self.m_idx+self.capacity-1)%self.capacity])

	# def sample(self, batch_size):
	#	 return random.sample(self.memory, batch_size)

	# def __len__(self):
	#	 return len(self.memory)

class action_provider(object):
	def __init__(self):
		self.a = [0,1,2,3,4,5,6]
		self.idx = -1

	def get(self):
		self.idx = (self.idx + 1) % len(self.a)
		return self.a[self.idx]

class node(object):
	def __init__(self, action_seq, total_reward):
		self.action_seq = action_seq
		self.total_reward = total_reward

class stack_info(node):
	def __init__(self, action_seq, total_reward, current_action):
		super(stack_info, self).__init__(action_seq, total_reward)
		self.current_action = current_action

class state_hash(object):
	def __init__(self):
		self.visit_states = set()

	def record_visit(self, s):
		#s.flags.writeable = False
		self.visit_states.add(s.data)
		#print(s)

	def visited(self, s):
		return s.data in self.visit_states

class exploration(object):
	def __init__(self):
		self.game_state = GameState(display=False)
		self.trajectories = trajectory_collection()

	def random_exploration(self):
		#ap = action_provider()
		for _ in xrange(1000):
			total_reward = 0.0
			self.game_state.reset()
			while True:
				if self.game_state.terminal:
					self.trajectories.add_unit(self.game_state.s_t, -1, 0)
					#tmp_len = len(self.trajectories.current_tj)
					print('Len =',len(self.trajectories.current_tj), 'Total Reward =', total_reward)
					self.trajectories.done()
					#self.trajectories.print_last()
					# if tmp_len==10003:
					# 	self.trajectories.print_last_action_seq()
					break
				action = np.random.randint(ACTION_SIZE)
				#action = ap.get()
				self.game_state.process(action)
				self.trajectories.add_unit(self.game_state.s_t, action, self.game_state.reward)
				total_reward += self.game_state.reward
				self.game_state.update()

	def bfs(self):
		my_hash = state_hash()

		q = Queue()
		q.put(node([], 0)) # initial state
		while True:
			if q.empty():
				break
			u = q.get_nowait()
			#print(u.action_seq, u.total_reward)
			#print('###', id(u))
			for action in xrange(ACTION_SIZE):
				# go to that state
				self.game_state.reset()
				for act in u.action_seq:
					self.game_state.process(act)
					self.game_state.update()
				# try actions
				self.game_state.process(action)
				self.game_state.update()
				if self.game_state.terminal:
					# for act in u.action_seq:
					# 	self.trajectories.add_unit(None, act, )
					print('Done ', len(u.action_seq), u.action_seq, action, u.total_reward + self.game_state.reward)
					#print(id(u))
					continue
				# if len(u.action_seq)==1 and u.action_seq[0]==2 and action==4:
				# 	print('here')
				# 	print(self.game_state.s_t)
				# 	exit()
				self.game_state.s_t.flags.writeable = False
				if not my_hash.visited(self.game_state.s_t):
					# if len(u.action_seq)==1 and u.action_seq[0]==2 and action==4:
					# 	print('here2')
					my_hash.record_visit(self.game_state.s_t)
					v = copy.deepcopy(u)
					v.action_seq.append(action)
					v.total_reward += self.game_state.reward
					#print('----',id(v))
					q.put(v)

	def bfs_gym(self):
		env = gym.make('MountainCar-v0')
		action_size = env.action_space.n
		my_hash = state_hash()

		q = Queue()
		q.put(node([], 0)) # initial state
		#best_path = None
		#max_r = -1000
		cnt = 0
		while True:
			cnt += 1
			if cnt % 2000 == 0:
				print(cnt)
			if q.empty():
				break
			u = q.get_nowait()
			#print(u.action_seq, u.total_reward)
			#print('###', id(u))
			for action in xrange(action_size):
				# go to that state
				env.reset()
				for act in u.action_seq:
					env.step(act)
					#acc_r += reward
				# try actions
				ob, reward, done, _ = env.step(action)
				#acc_r += reward
				if done:
					# for act in u.action_seq:
					# 	self.trajectories.add_unit(None, act, )
					print('Done ', len(u.action_seq), u.action_seq, action, u.total_reward + reward)
					#print(id(u))
					return
				# if len(u.action_seq)==1 and u.action_seq[0]==2 and action==4:
				# 	print('here')
				# 	print(self.game_state.s_t)
				# 	exit()
				ob = ob * 1000
				ob = ob.astype(int)
				ob.flags.writeable = False
				if not my_hash.visited(ob):
					# if len(u.action_seq)==1 and u.action_seq[0]==2 and action==4:
					# 	print('here2')
					my_hash.record_visit(ob)
					v = copy.deepcopy(u)
					v.action_seq.append(action)
					v.total_reward += reward
					#print('----',id(v))
					q.put(v)

	def dfs(self):
		my_hash = state_hash()

		q = LifoQueue()
		q.put(stack_info([], 0, 0)) # initial state
		while not q.empty():
			u = q.get_nowait()
			action = u.current_action
			if u.current_action < ACTION_SIZE - 1:
				u.current_action += 1
				q.put(u)
			# go to that state
			self.game_state.reset()
			for act in u.action_seq:
				self.game_state.process(act)
				self.game_state.update()
			# try actions
			self.game_state.process(action)
			self.game_state.update()
			if self.game_state.terminal:
				print('Done ', len(u.action_seq), u.action_seq, action, u.total_reward + self.game_state.reward)
				continue
			self.game_state.s_t.flags.writeable = False
			if not my_hash.visited(self.game_state.s_t):
				my_hash.record_visit(self.game_state.s_t)
				v = copy.deepcopy(u)
				v.action_seq.append(action)
				v.total_reward += self.game_state.reward
				v.current_action = 0
				q.put(v)


if __name__ == "__main__":
	e = exploration()
	#e.random_exploration()
	e.bfs_gym()
	#e.dfs()
	#print('Total Interaction = ', e.game_state.game.interact_cnt)


# result of Mountain car

# Done  101 [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2] 1 -102.0
