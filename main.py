#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import logging
from logging.config import fileConfig

from OpenGL.GL import *
import glfw

from shader import Shader
from text import Text


class MainView:
	def __init__(self):
		fileConfig('log.conf')
		self.logger = logging.getLogger(type(self).__name__)

		self.resolution = (800,450)
		self.target_fps = 60
		self.frame_render_time = 1/self.target_fps

		self.init_window()
		self.get_gl_info()
		self.init_shaders()
		self.main_loop()

	def get_gl_info(self):
		self.logger.info('Vendor    : {}'.format(glGetString(GL_VENDOR).decode()))
		self.logger.info('Renderer  : {}'.format(glGetString(GL_RENDERER).decode()))
		self.logger.info('Version   : {}'.format(glGetString(GL_VERSION).decode()))
		self.logger.info('SL Version: {}'.format(glGetString(GL_SHADING_LANGUAGE_VERSION).decode()))
		#self.logger.debug('Extensions: {}'.format(glGetString(GL_EXTENSIONS).decode()))

	def init_shaders(self):
		self.shader = Shader({GL_VERTEX_SHADER:'shader.vert', GL_GEOMETRY_SHADER:'shader.geom', GL_FRAGMENT_SHADER:'shader.frag'})
		self.shader.create_program()
		self.shader.add_uniforms(['resolution', 'time'])
		self.logger.debug('Shader program initialized')

	def init_window(self):
		glfw.init()
		self.window = glfw.create_window(*self.resolution, 'PyGL', None, None)
		glfw.make_context_current(self.window)
		glfw.set_window_size_callback(self.window, self.resize)
		glfw.set_key_callback(self.window, self.keyboard_input)
		glClearColor(0,0,0,1)
		self.target_frame_time = 1/self.target_fps

		self.fps_viewer = Text('Hack-Regular.ttf', size=20)
		glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
		glEnable(GL_BLEND)
		glEnable(GL_COLOR_MATERIAL)
		glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
		glEnable(GL_TEXTURE_2D)

		self.logger.debug('Window initialized')

	def resize(self, win, width, height):
		#self.logger.debug('Window resized: {}x{}'.format(width, height))
		self.resolution = (width, height)
		glViewport(0, 0, *self.resolution)

	def keyboard_input(self, win, key, scancode, action, mods):
		self.logger.debug('key: {}, scancode: {}, action: {}, mods: {}'.format(key, scancode, action, mods))
		if ((key == glfw.KEY_ESCAPE) or (key == glfw.KEY_F4 and mods == glfw.MOD_ALT) and action == glfw.PRESS):
			glfw.set_window_should_close(self.window, True)
			self.logger.info('Exiting')

	def wait_for_frame_end(self, frame_start_time):
		frame_render_time = glfw.get_time()-frame_start_time
		#self.logger.debug('Frame render time: {:.1f} ms ({:.1f}%)'.format(1000*frame_render_time, frame_render_time/self.target_frame_time*100))
		self.frame_render_time = frame_render_time
		sleep_time = self.target_frame_time - frame_render_time
		if sleep_time > 0:
			time.sleep(sleep_time)

	def main_loop(self):
		while not glfw.window_should_close(self.window):
			frame_start_time = glfw.get_time()
			glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

			# Draw scene
			self.shader.bind()
			self.shader.set_uniforms({'resolution':self.resolution, 'time':glfw.get_time()})
			glDrawArrays(GL_POINTS, 0, 1) # dummy vbo
			self.shader.unbind()

			# Draw text
			glPushMatrix()
			glTranslate(-.9, .8, 0)
			glScale(1/self.resolution[0], 1/self.resolution[1], 1)
			self.fps_viewer.draw('{:4.0f}/{:2.0f} FPS, {:4.1f} ms ({:3.0f}%)'.format(1/self.frame_render_time, self.target_fps, self.frame_render_time*1000, self.frame_render_time/self.target_frame_time*100))
			glPopMatrix()

			glfw.swap_buffers(self.window)
			self.wait_for_frame_end(frame_start_time)
			glfw.poll_events()
		glfw.terminate()


if __name__ == '__main__':
	mv = MainView()