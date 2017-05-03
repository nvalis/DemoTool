#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import logging
from logging.config import fileConfig
import numpy as np

from OpenGL.GL import *
import glfw

from shader import Shader
from camera import Camera
from text import Text
from ui import UI


class MainView:
	def __init__(self):
		fileConfig('log.conf')
		self.logger = logging.getLogger(type(self).__name__)

		self.resolution = np.array([800,450])
		self.target_fps = 60
		self.frame_render_time = 1/self.target_fps

		self.init_window()
		self.get_gl_info()
		self.init_shader()
		self.init_camera()
		self.main_loop()

	def get_gl_info(self):
		self.logger.info('Vendor    : {}'.format(glGetString(GL_VENDOR).decode()))
		self.logger.info('Renderer  : {}'.format(glGetString(GL_RENDERER).decode()))
		self.logger.info('Version   : {}'.format(glGetString(GL_VERSION).decode()))
		self.logger.info('SL Version: {}'.format(glGetString(GL_SHADING_LANGUAGE_VERSION).decode()))
		#self.logger.debug('Extensions: {}'.format(glGetString(GL_EXTENSIONS).decode()))

	def get_shader_time(self):
		return os.path.getmtime('shaders/shader.frag')

	def init_shader(self):
		self.shader = Shader({GL_VERTEX_SHADER:'shaders/shader.vert', GL_GEOMETRY_SHADER:'shaders/shader.geom', GL_FRAGMENT_SHADER:'shaders/shader.frag'})
		self.shader.create()
		self.shader_time = self.get_shader_time()
		self.freeze_time = False
		self.time = 0.
		self.logger.debug('Shader program initialized')

	def init_camera(self):
		self.camera = Camera(self)

	def init_window(self):
		glfw.init()
		self.window = glfw.create_window(*self.resolution, 'PyGL', None, None)
		glfw.make_context_current(self.window)
		glfw.set_window_size_callback(self.window, self.resize)
		glfw.set_key_callback(self.window, self.keyboard_input)
		glfw.set_scroll_callback(self.window, self.scroll_input)
		glfw.set_cursor_pos_callback(self.window, self.mouse_position_input)
		glClearColor(0,0,0,1)
		self.target_frame_time = 1/self.target_fps

		self.ui = UI(self)
		self.logger.debug('Window initialized')

	def resize(self, win, width, height):
		#self.logger.debug('Window resized: {}x{}'.format(width, height))
		self.resolution = np.array([width, height])
		glViewport(0, 0, *self.resolution)

	def keyboard_input(self, win, key, scancode, action, mods):
		#self.logger.debug('key: {}, scancode: {}, action: {}, mods: {}'.format(key, scancode, action, mods))
		if (key == glfw.KEY_ESCAPE) or (mods == glfw.MOD_ALT and key == glfw.KEY_F4) and action == glfw.PRESS:
			glfw.set_window_should_close(self.window, True)
			self.logger.info('Exiting')
		if key == glfw.KEY_H and action == glfw.PRESS:
			self.ui.toggle_visibility()
			self.logger.debug('Toggle UI')
		if key == glfw.KEY_W and action != glfw.RELEASE:
			self.camera.move_forward()
		if key == glfw.KEY_A and action != glfw.RELEASE:
			self.camera.move_left()
		if key == glfw.KEY_S and action != glfw.RELEASE:
			self.camera.move_backward()
		if key == glfw.KEY_D and action != glfw.RELEASE:
			self.camera.move_right()
		if key == glfw.KEY_Q and action != glfw.RELEASE:
			self.camera.move_up()
		if key == glfw.KEY_E and action != glfw.RELEASE:
			self.camera.move_down()
		if key == glfw.KEY_R and action == glfw.PRESS:
			self.camera.reset()
		if key == glfw.KEY_P and action == glfw.PRESS:
			self.freeze_time = not self.freeze_time
			self.logger.info('Toggle time freeze')
		if key == glfw.KEY_F and action == glfw.PRESS:
			self.camera.toggle_look_mode()
			self.logger.info('Toggle camera look mode')
		if key == glfw.KEY_T and action == glfw.PRESS:
			self.ui.toggle_composition_overlay()
			self.logger.info('Toggle composition overlay')

	def scroll_input(self, win, x, y):
		if y > 0:
			self.camera.accelerate()
		elif y < 0:
			self.camera.decelerate()

	def mouse_position_input(self, win, x, y):
		if self.camera.look_mode:
			self.camera.look(x, y)

	def wait_for_frame_end(self, frame_start_time):
		frame_render_time = glfw.get_time()-frame_start_time
		#self.logger.debug('Frame render time: {:.1f} ms ({:.1f}%)'.format(1000*frame_render_time, frame_render_time/self.target_frame_time*100))
		self.frame_render_time = frame_render_time
		sleep_time = self.target_frame_time - frame_render_time
		if sleep_time > 0:
			time.sleep(sleep_time)

	def check_for_shader_change(self):
		current_time = self.get_shader_time()
		if current_time != self.shader_time:
			self.shader_time = current_time
			self.shader.create()

	def main_loop(self):
		while not glfw.window_should_close(self.window):
			self.check_for_shader_change()
			frame_start_time = glfw.get_time()
			if not self.freeze_time:
				self.time = frame_start_time

			glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

			# Draw scene
			self.shader.bind()
			self.shader.set_uniforms(
				{
					'resolution':self.resolution,
					'time':self.time,
					'camera_position':self.camera.position,
					'camera_rotation':self.camera.rotation.mat3()
				}
			)
			glDrawArrays(GL_POINTS, 0, 1) # dummy vbo
			self.shader.unbind()

			# Draw UI
			self.ui.draw(
				{
					'fps_label':'{:4.0f}/{:2.0f} FPS, {:4.1f} ms ({:3.0f}%)'.format(1/self.frame_render_time, self.target_fps, self.frame_render_time*1000, self.frame_render_time/self.target_frame_time*100),
					'time_label':'Time: {:4.2f} s {}'.format(self.time, '[f]' if self.freeze_time else ''),
					'camera_label':'Camera: [{:5.2f}, {:5.2f}, {:5.2f}] ({:3.0f}%), [{:5.1f}, {:4.1f}]'.format(*self.camera.position, self.camera.speed*100, np.degrees(self.camera.yaw), np.degrees(self.camera.pitch))
				}
			)

			glfw.swap_buffers(self.window)
			self.wait_for_frame_end(frame_start_time)
			glfw.poll_events()

		glfw.terminate()

if __name__ == '__main__':
	mv = MainView()