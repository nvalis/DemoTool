#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import logging
from logging.config import fileConfig

from OpenGL.GL import *
import glfw

from shader import Shader


class MainView:
	def __init__(self):
		fileConfig('log.conf')
		self.logger = logging.getLogger(type(self).__name__)

		self.resolution = (800,600)
		self.target_FPS = 60

		self.init_window()
		self.init_shaders()
		self.main_loop()

	def init_shaders(self):
		self.shader = Shader({GL_VERTEX_SHADER:'shader.vert', GL_GEOMETRY_SHADER:'shader.geom', GL_FRAGMENT_SHADER:'shader.frag'})
		self.shader.create_program()
		self.shader.add_uniforms([('resolution', glUniform2fv, 1), ('time', glUniform1f)])
		self.logger.debug('Shader program initialized')

	def init_window(self):
		glfw.init()
		self.window = glfw.create_window(*self.resolution, 'PyGL', None, None)
		glfw.make_context_current(self.window)
		glfw.set_window_size_callback(self.window, self.resize)
		glClearColor(0,0,0,1)
		self.target_frame_time = 1/self.target_FPS
		self.logger.debug('Window initialized')

	def resize(self, win, width, height):
		#self.logger.debug('Window resized: {}x{}'.format(width, height))
		self.resolution = (width, height)
		glViewport(0, 0, *self.resolution)

	def wait_for_frame_end(self, frame_start_time):
		frame_render_time = glfw.get_time()-frame_start_time
		#self.logger.debug('Frame render time: {:.1f} ms ({:.1f}%)'.format(1000*frame_render_time, frame_render_time/self.target_frame_time*100))
		sleep_time = self.target_frame_time - frame_render_time
		if sleep_time > 0:
			time.sleep(sleep_time)

	def main_loop(self):
		while not glfw.window_should_close(self.window):
			frame_start_time = glfw.get_time()
			glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
			glUseProgram(self.shader.program)
			self.shader.set_uniforms({'resolution':self.resolution, 'time':glfw.get_time()})
			glDrawArrays(GL_POINTS, 0, 1) # dummy vbo
			glUseProgram(0)
			glfw.swap_buffers(self.window)
			glfw.poll_events()
			self.wait_for_frame_end(frame_start_time)
		glfw.terminate()


if __name__ == '__main__':
	mv = MainView()