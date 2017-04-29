# -*- coding: utf-8 -*-

import time
import logging

from OpenGL.GL import *

class Shader:
	def __init__(self, shader_paths):
		self.logger = logging.getLogger(type(self).__name__)

		self.shader_paths = shader_paths
		self.uniform_locations = {}
		self._load_shader_code(*self.shader_paths.keys())

	def __str__(self):
		return '<Shader: {}>'.format(', '.join(['{}:{}'.format(s.name, p) for s, p in self.shader_paths.items()]))

	def _load_shader_code(self, *shaders):
		self.code = {}
		for shader in shaders:
			self.code[shader] = open(self.shader_paths[shader]).read()

	def _create_shader(self, shader_string, shader_type):
		shader = glCreateShader(shader_type)
		glShaderSource(shader, shader_string)
		glCompileShader(shader)
		self._check_shader_status(shader)
		return shader

	def _check_shader_status(self, shader):
		if glGetShaderiv(shader, GL_COMPILE_STATUS) != GL_TRUE:
			log = glGetShaderInfoLog(shader)
			glDeleteShader(shader)
			self.logger.critical('Error compiling shader')
			print(log.decode())
			raise RuntimeError('Failed to compile shader')
		else:
			self.logger.debug('Shader compiling successful')

	def _check_program_status(self, program):
		if glGetProgramiv(program, GL_LINK_STATUS) != GL_TRUE:
			log = glGetProgramInfoLog(program)
			glDeleteProgram(program)
			self.logger.critical('Error linking program')
			print(log.decode())
			raise RuntimeError('Failed to link program')
		else:
			self.logger.debug('Program linking successful')

	def create_program(self):
		start = time.time()

		'''
		# mixed program pipeline
		# from: https://www.khronos.org/opengl/wiki/Shader_Compilation#Mixing_a_single-_and_a_multi-stage_program
		self.vert_geom_program = glCreateProgram()
		self.frag_program = glCreateProgram()
		glProgramParameteri(self.vert_geom_program, GL_PROGRAM_SEPARABLE, GL_TRUE)
		glProgramParameteri(self.frag_program, GL_PROGRAM_SEPARABLE, GL_TRUE)

		vert = self._create_shader(self.code[GL_VERTEX_SHADER], GL_VERTEX_SHADER)
		geom = self._create_shader(self.code[GL_GEOMETRY_SHADER], GL_GEOMETRY_SHADER)
		frag = self._create_shader(self.code[GL_FRAGMENT_SHADER], GL_FRAGMENT_SHADER)

		glAttachShader(self.vert_geom_program, vert)
		glAttachShader(self.vert_geom_program, geom)
		glAttachShader(self.frag_program, frag)

		glBindFragDataLocation(self.frag_program, 0, 'FragColor')

		glLinkProgram(self.vert_geom_program)
		self._check_program_status(self.vert_geom_program)
		glLinkProgram(self.frag_program)
		self._check_program_status(self.frag_program)

		glDetachShader(self.vert_geom_program, vert)
		glDetachShader(self.vert_geom_program, geom)
		glDeleteShader(vert)
		glDeleteShader(geom)
		glDetachShader(self.frag_program, frag)
		glDeleteShader(frag)

		self.program = glGenProgramPipelines(1)
		glUseProgramStages(self.program, GL_VERTEX_SHADER_BIT | GL_GEOMETRY_SHADER_BIT, self.vert_geom_program)
		glUseProgramStages(self.program, GL_FRAGMENT_SHADER_BIT, self.frag_program)
		'''

		# "fixed" pipeline
		self.program = glCreateProgram()

		shaders = [self._create_shader(self.code[t], t) for t in self.shader_paths.keys()]

		for s in shaders: glAttachShader(self.program, s)

		glBindFragDataLocation(self.program, 0, 'FragColor')

		glLinkProgram(self.program)
		self._check_program_status(self.program)

		for s in shaders:
			glDetachShader(self.program, s)
			glDeleteShader(s)

		self.logger.info('Compiled the shader program in {:.1f} ms'.format((time.time()-start)*1000))

	def bind(self):
		glUseProgram(self.program)

	def unbind(self):
		glUseProgram(0)

	def add_uniform(self, uniform_name):
		self.uniform_locations[uniform_name] = glGetUniformLocation(self.program, uniform_name)

	def add_uniforms(self, uniform_list):
		for u in uniform_list:
			self.add_uniform(u)

	def get_uniform_location(self, uniform_name):
		return self.uniform_locations[uniform_name]

	def set_uniform(self, name, vals):
		if isinstance(vals, (int,float)):
			vals = (vals,)

		l = len(vals)
		setter = {1:glUniform1f, 2:glUniform2f, 3:glUniform3f, 4:glUniform4f}[l]
		if l in range(1,5):
			setter(self.uniform_locations[name], *vals)
		else:
			self.logger.warning('Nonvalid length for uniform \'{}\': {}'.format(uniform_name, l))

	def set_uniforms(self, uniform_dict):
		for name, value in uniform_dict.items():
			self.set_uniform(name, value)

if __name__ == '__main__':
	import pygame

	pygame.init()
	test = Shader({GL_VERTEX_SHADER:'shader.vert', GL_GEOMETRY_SHADER:'shader.geom', GL_FRAGMENT_SHADER:'shader.frag'})
	print(test)
	test.create_program()
	print(test.program)