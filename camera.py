# -*- coding: utf-8 -*-

import glfw

import logging
import numpy as np

from quaternion import *

class Camera:
	def __init__(self, view):
		self.logger = logging.getLogger(type(self).__name__)
		self.view = view

		# movement
		self.position = np.zeros(3)
		self.speed = 0.05

		# rotation
		self.look_mode = False
		self.yaw, self.pitch = 0, 0
		self.rotation = Quaternion()
		self.sensitivity = np.array([1.,1.])

	def move_forward(self):
		self.position += self.rotation.front()*self.speed

	def move_backward(self):
		self.position += -self.rotation.front()*self.speed

	def move_left(self):
		self.position += -self.rotation.right()*self.speed

	def move_right(self):
		self.position += self.rotation.right()*self.speed

	def move_up(self):
		self.position += self.rotation.up()*self.speed

	def move_down(self):
		self.position += -self.rotation.up()*self.speed

	def accelerate(self):
		self.speed *= 1.2

	def decelerate(self):
		self.speed /= 1.2

	def toggle_look_mode(self):
		self.look_mode = not self.look_mode
		if self.look_mode:
			glfw.set_input_mode(self.view.window, glfw.CURSOR, glfw.CURSOR_DISABLED)
		else:
			glfw.set_input_mode(self.view.window, glfw.CURSOR, glfw.CURSOR_NORMAL)
		self.mouse_pos = np.array(glfw.get_cursor_pos(self.view.window))/self.view.resolution

	def look(self, x, y):
		self.now_mouse_pos = np.array([x,y])/self.view.resolution # normalized mouse pos
		mouse_delta = (self.now_mouse_pos-self.mouse_pos) * self.sensitivity
		self.mouse_pos = self.now_mouse_pos
		self.yaw += mouse_delta[0]
		self.pitch += mouse_delta[1]

		# clamp angles
		if self.pitch > np.pi/2: self.pitch = np.pi/2
		if self.pitch < -np.pi/2: self.pitch = -np.pi/2
		if self.yaw < 0: self.yaw += 2*np.pi
		if self.yaw > 2*np.pi: self.yaw -= 2*np.pi

		yaw_q = axisangle_to_q(np.array([0,1,0], 'f'), self.yaw)
		pitch_q = axisangle_to_q(np.array([1,0,0], 'f'), self.pitch)

		#print('{:4.1f} {:4.1f}'.format(np.degrees(self.pitch), np.degrees(self.yaw)))
		self.rotation = pitch_q * yaw_q

	def reset(self):
		self.position = np.zeros(3)
		self.pitch, self.yaw = 0, 0
		self.rotation = Quaternion()
		self.speed = .1
		self.logger.info('Reset camera')