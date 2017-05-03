# -*- coding: utf-8 -*-

import numpy as np

from OpenGL.GL import *
from freetype import *

# code from: https://github.com/rougier/freetype-py/blob/master/examples/opengl.py


class Text:
	def __init__(self, position, font_filename='assets/Hack-Regular.ttf', size=30):
		self.position = position
		self.face = Face(font_filename)
		self.face.set_char_size(size*64)
		if not self.face.is_fixed_width:
			raise 'Font is not monotype'

		# Determine largest glyph size
		width, height, ascender, descender = 0, 0, 0, 0
		for c in range(32,128):
			self.face.load_char(chr(c), FT_LOAD_RENDER | FT_LOAD_FORCE_AUTOHINT)
			bitmap    = self.face.glyph.bitmap
			width     = max(width, bitmap.width)
			ascender  = max(ascender, self.face.glyph.bitmap_top)
			descender = max(descender, bitmap.rows-self.face.glyph.bitmap_top)
		height = ascender+descender

		# Generate texture data
		Z = np.zeros((height*6, width*16), dtype=np.ubyte)
		for j in range(6):
			for i in range(16):
				self.face.load_char(chr(32+j*16+i), FT_LOAD_RENDER|FT_LOAD_FORCE_AUTOHINT)
				bitmap = self.face.glyph.bitmap
				x = i*width  + self.face.glyph.bitmap_left
				y = j*height + ascender-self.face.glyph.bitmap_top
				Z[y:y+bitmap.rows,x:x+bitmap.width].flat = bitmap.buffer

		# Bound texture
		self.texid = glGenTextures(1)
		glBindTexture(GL_TEXTURE_2D, self.texid)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
		glTexImage2D(GL_TEXTURE_2D, 0, GL_ALPHA, Z.shape[1], Z.shape[0], 0, GL_ALPHA, GL_UNSIGNED_BYTE, Z)

		# Generate display lists
		dx, dy = width/float(Z.shape[1]), height/float(Z.shape[0])
		self.base = glGenLists(8*16)
		for i in range(8*16):
			c = chr(i)
			x = i%16
			y = i//16-2
			glNewList(self.base+i, GL_COMPILE)
			if (c == '\n'):
				glPopMatrix()
				glTranslatef(0, -height, 0)
				glPushMatrix()
			elif (c == '\t'):
				glTranslatef(4*width, 0, 0)
			elif (i >= 32):
				glBegin(GL_QUADS)
				glTexCoord2f((x  )*dx, (y+1)*dy ), glVertex(0,     -height)
				glTexCoord2f((x  )*dx, (y  )*dy ), glVertex(0,     0)
				glTexCoord2f((x+1)*dx, (y  )*dy ), glVertex(width, 0)
				glTexCoord2f((x+1)*dx, (y+1)*dy ), glVertex(width, -height)
				glEnd()
				glTranslatef(width, 0, 0)
			glEndList()

	def draw(self, text):
		glBindTexture(GL_TEXTURE_2D, self.texid)
		glColor(1,1,1,1)
		glPushMatrix()
		glListBase(self.base)
		glCallLists([ord(c) for c in text])
		glPopMatrix()
