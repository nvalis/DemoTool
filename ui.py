# -*- coding: utf-8 -*-

import logging
from OpenGL.GL import *

from text import Text
from shader import Shader

class UI:
	def __init__(self, view):
		self.logger = logging.getLogger(type(self).__name__)
		self.view = view

		self.enabled = True

		self.init_opengl()
		self.elements = {
			'time_label':Text((.01, .99)),
			'fps_label':Text((.71, .99)),
			'camera_label':Text((.01, .04))
		}

		self.composition_overlay_enabled = True
		self.overlay_shader = Shader({GL_VERTEX_SHADER:'shaders/shader.vert', GL_GEOMETRY_SHADER:'shaders/shader.geom', GL_FRAGMENT_SHADER:'shaders/composition.frag'})
		self.overlay_shader.create()
		self.logger.debug('Initialized UI')

	def init_opengl(self):
		glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
		glEnable(GL_BLEND)
		glEnable(GL_COLOR_MATERIAL)
		glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
		glEnable(GL_TEXTURE_2D)

	def toggle_visibility(self):
		self.enabled = not self.enabled

	def toggle_composition_overlay(self):
		self.composition_overlay_enabled = not self.composition_overlay_enabled

	def draw_composition_overlay(self):
		self.overlay_shader.bind()
		self.overlay_shader.set_uniforms(
			{
				'resolution':self.view.resolution,
				'time':0.,
			}
		)
		glDrawArrays(GL_POINTS, 0, 1) # dummy vbo
		self.overlay_shader.unbind()

	def draw(self, values_dict):
		if not self.enabled: return
		ar = self.view.resolution[0]/self.view.resolution[1]
		glPushMatrix()
		glTranslatef(-1,-1,0)
		glScale(2,2,1) # -> [0,1]x[0,1]

		for name, elem in self.elements.items():
			glPushMatrix()
			glTranslatef(*elem.position, 0)
			#glScale(1/self.view.resolution[0], 1/self.view.resolution[1], 1)
			glScale(1/2000, 1/2000*ar, 1)
			elem.draw(values_dict[name])
			glPopMatrix()

		if self.composition_overlay_enabled:
			self.draw_composition_overlay()

		glPopMatrix()