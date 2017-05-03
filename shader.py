# -*- coding: utf-8 -*-

import time
import logging
import numpy as np
from OpenGL.GL import *

class Shader:
	def __init__(self, shader_paths):
		self.logger = logging.getLogger(type(self).__name__)

		self.shader_paths = shader_paths
		self.program = None
		self.uniform_locations = {}
		self._load_shader_code(*self.shader_paths.keys())

	def __str__(self):
		return '<Shader: {}>'.format(', '.join(['{}:{}'.format(s.name, p) for s, p in self.shader_paths.items()]))

	def _load_shader_code(self, *shaders):
		self.code = {}
		for shader in shaders:
			self.code[shader] = open(self.shader_paths[shader]).read()

	def _compile_shader(self, shader_string, shader_type):
		shader = glCreateShader(shader_type)
		glShaderSource(shader, shader_string)
		glCompileShader(shader)
		s = self._check_shader_status(shader)
		if s:
			self.logger.error(s.replace('\n', '\n\t'))
			raise RuntimeError('Failed to compile {}'.format(shader_type))
		return shader

	def _check_shader_status(self, shader):
		if glGetShaderiv(shader, GL_COMPILE_STATUS) != GL_TRUE:
			log = glGetShaderInfoLog(shader)
			glDeleteShader(shader)
			return log.decode()

	def _check_program_status(self, program):
		if glGetProgramiv(program, GL_LINK_STATUS) != GL_TRUE:
			log = glGetProgramInfoLog(program)
			glDeleteProgram(program)
			return log.decode()

	def _create_program(self):
		start = time.time()

		'''
		# mixed program pipeline
		# from: https://www.khronos.org/opengl/wiki/Shader_Compilation#Mixing_a_single-_and_a_multi-stage_program
		self.vert_geom_program = glCreateProgram()
		self.frag_program = glCreateProgram()
		glProgramParameteri(self.vert_geom_program, GL_PROGRAM_SEPARABLE, GL_TRUE)
		glProgramParameteri(self.frag_program, GL_PROGRAM_SEPARABLE, GL_TRUE)

		vert = self._compile_shader(self.code[GL_VERTEX_SHADER], GL_VERTEX_SHADER)
		geom = self._compile_shader(self.code[GL_GEOMETRY_SHADER], GL_GEOMETRY_SHADER)
		frag = self._compile_shader(self.code[GL_FRAGMENT_SHADER], GL_FRAGMENT_SHADER)

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

		program = glGenProgramPipelines(1)
		glUseProgramStages(program, GL_VERTEX_SHADER_BIT | GL_GEOMETRY_SHADER_BIT, self.vert_geom_program)
		glUseProgramStages(program, GL_FRAGMENT_SHADER_BIT, self.frag_program)
		'''

		# "fixed" pipeline
		shaders = []
		for t in self.shader_paths.keys():
			try:
				s = self._compile_shader(self.code[t], t)
				shaders.append(s)
			except RuntimeError:
				self.logger.error('Failed to compile {} shader!'.format(t))
				return

		program = glCreateProgram()
		for s in shaders: glAttachShader(program, s)

		glBindFragDataLocation(program, 0, 'FragColor')

		glLinkProgram(program)
		try:
			self._check_program_status(program)
		except RuntimeError:
			self.logger.error('Failed to create program!')
			return

		for s in shaders:
			glDetachShader(program, s)
			glDeleteShader(s)

		self.logger.info('Compiled the shader program in {:.1f} ms'.format((time.time()-start)*1000))
		return program

	def create(self):
		if self.program:
			glDeleteProgram(self.program)
			self.program = None
		self._load_shader_code(*self.shader_paths.keys())
		program = self._create_program()
		if program:
			self.program = program
		self.parse_uniforms()

	def bind(self):
		if self.program:
			glUseProgram(self.program)

	def unbind(self):
		glUseProgram(0)

	def parse_uniforms(self):
		for l in self.code[GL_FRAGMENT_SHADER].splitlines():
			if l.startswith('uniform'):
				self._add_uniform(l.split()[-1].replace(';', ''))
		self.logger.debug('Parsed uniforms: {}'.format(', '.join(self.uniform_locations.keys())))

	def _add_uniform(self, uniform_name):
		self.uniform_locations[uniform_name] = glGetUniformLocation(self.program, uniform_name)

	def set_uniform(self, name, vals):
		# TODO: implement setting of matrices?
		if isinstance(vals, (int,float)): vals = np.array([vals])
		dim = len(vals.shape)
		if dim == 1: # scalar/vector
			l = vals.shape[0]
			if l in range(1,5):
				setter = {1:glUniform1f, 2:glUniform2f, 3:glUniform3f, 4:glUniform4f}
				if name in self.uniform_locations:
					setter[l](self.uniform_locations[name], *vals)
				else:
					self.logger.error('No such uniform \'{}\''.format(name))
			else:
				self.logger.warning('Nonvalid shape for uniform \'{}\': {}'.format(uniform_name, vals.shape))
		elif dim == 2: # matrix
			l1, l2 = vals.shape[0], vals.shape[1]
			if l1 in range(2,5) and l2 in range(2,5):
				setter = {(2,2):glUniformMatrix2fv, (3,3):glUniformMatrix3fv, (4,4):glUniformMatrix4fv, (2,3):glUniformMatrix2x3fv, (3,2):glUniformMatrix3x2fv, (2,4):glUniformMatrix2x4fv, (4,2):glUniformMatrix4x2fv, (3,4):glUniformMatrix3x4fv, (4,3):glUniformMatrix4x3fv}
				if name in self.uniform_locations:
					setter[l1,l2](self.uniform_locations[name], 1, False, vals)
				else:
					self.logger.error('No such uniform \'{}\''.format(name))
			else:
				self.logger.warning('Nonvalid shape for uniform \'{}\': {}'.format(uniform_name, vals.shape))

	def set_uniforms(self, uniform_dict):
		for name, value in uniform_dict.items():
			self.set_uniform(name, value)

if __name__ == '__main__':
	import pygame

	pygame.init()
	shader = Shader({GL_VERTEX_SHADER:'shader.vert', GL_GEOMETRY_SHADER:'shader.geom', GL_FRAGMENT_SHADER:'shader.frag'})
	print(shader)
	shader.create()