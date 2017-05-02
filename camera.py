# -*- coding: utf-8 -*-

import logging
import numpy as np

class Camera:
	def __init__(self):
		self.logger = logging.getLogger(type(self).__name__)

		self.offset = np.array([0.,0.,0.])
		self.speed = 1.

	def move_forward(self):
		self.offset -= np.array([0,0,self.speed])

	def move_backward(self):
		self.offset += np.array([0,0,self.speed])

	def move_left(self):
		self.offset -= np.array([self.speed,0,0])

	def move_right(self):
		self.offset += np.array([self.speed,0,0])

	def move_up(self):
		self.offset += np.array([0,self.speed,0])

	def move_down(self):
		self.offset -= np.array([0,self.speed,0])

	def accelerate(self):
		self.speed *= 1.2

	def decelerate(self):
		self.speed /= 1.2

	def reset(self):
		self.offset = np.array([0.,0.,0.])
		self.speed = .1
		self.logger.info('Reset camera')