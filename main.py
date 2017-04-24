#!/usr/bin/env python3

import numpy as np

import pygame
from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.GLUT import *

class MainView:
	def __init__(self):
		self.resolution = (800,600)
		self.target_fps = 60

		self.init_window()
		self.init_shaders()
		self.main_loop()

	def init_window(self):
		pygame.init()
		pygame.display.set_mode(self.resolution, pygame.OPENGL|pygame.DOUBLEBUF|pygame.NOFRAME|pygame.RESIZABLE)
		pygame.display.set_caption('PyGL')

	def init_shaders(self):
		geometry_shader = shaders.compileShader(open('shader.geom').readlines(), GL_GEOMETRY_SHADER)
		vertex_shader = shaders.compileShader(open('shader.vert').readlines(), GL_VERTEX_SHADER)
		fragment_shader = shaders.compileShader(open('shader.frag').readlines(), GL_FRAGMENT_SHADER)
		self.program = shaders.compileProgram(geometry_shader, vertex_shader, fragment_shader)
		self.uniforms = {
			'resolution':glGetUniformLocation(self.program, 'resolution')
		}

	def main_loop(self):
		self.clock = pygame.time.Clock()
		self.running = True
		while self.running:
			self.handle_events()
			self.draw()
			self.clock.tick(self.target_fps)
			#print('Current FPS: {:.1f}/{}'.format(self.clock.get_fps(), self.target_fps))

	def handle_events(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.running = False
			if event.type == pygame.VIDEORESIZE:
				self.resize(event.size)

	def resize(self, resolution):
		print('Window resized to {}x{}'.format(*resolution))
		self.resolution = resolution
		glViewport(0,0, *self.resolution)

	def draw(self):
		glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
		glUseProgram(self.program)
		glUniform2fv(self.uniforms['resolution'], 1, self.resolution)
		glDrawArrays(GL_POINTS, 0, 1) # dummy vbo
		pygame.display.flip()

if __name__ == '__main__':
	MainView()