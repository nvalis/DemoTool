# -*- coding: utf-8 -*-

import numpy as np

class Quaternion:
	def __init__(self, q=np.array([0,0,0,1],'f')):
		self.q = q

	def __repr__(self):
		return '<Quaternion [{:5.2f}, {:5.2f}, {:5.2f}, {:5.2f}]>'.format(*self.q)

	def __mul__(self, other):
		return q_dot(self, other)

	def right(self): return self.rotate(np.array([1,0,0], 'f'))
	def    up(self): return self.rotate(np.array([0,1,0], 'f'))
	def front(self): return self.rotate(np.array([0,0,-1], 'f'))

	def x(self): return self.q[0]
	def y(self): return self.q[1]
	def z(self): return self.q[2]
	def w(self): return self.q[3]
	def v(self): return self.q[:3]

	def normalize(self, tolerance=1e-4):
		mag2 = np.dot(self.q, self.q)
		if mag2 > tolerance and mag2 != 0.: self.q /= np.sqrt(mag2)

	def rotate(self, v):
		return np.dot(self.mat3(), v)

	def mat3(self):
		return self.mat4()[:3,:3]

	def mat4(self):
		self.normalize()
		x, y, z, w = self.q
		'''
		return np.array(
			[[1 - 2*y*y - 2*z*z, 2*x*y - 2*z*w, 2*x*z + 2*y*w, 0],
			[2*x*y + 2*z*w, 1 - 2*x*x - 2*z*z, 2*y*z - 2*x*w, 0],
			[2*x*z - 2*y*w, 2*y*z + 2*x*w, 1 - 2*x*x - 2*y*y, 0],
			[0, 0, 0, 1]],'f'
		)
		'''
		return np.array(
			[[1-2*y*y-2*z*z, 2*(x*y+z*w), 2*(x*z-y*w), 0],
			[2*(x*y-z*w), 1-2*x*x-2*z*z, 2*(y*z+x*w), 0],
			[2*(x*z+y*w), 2*(y*z-x*w), 1-2*x*x-2*y*y, 0],
			[0, 0, 0, 1]],'f'
		)

def q_dot(a, b):
	return Quaternion(np.append(
		a.w()*b.v() + b.w()*a.v() + np.cross(a.v(),b.v()),
		a.w()*b.w() - np.dot(a.v(),b.v())
	))

def axisangle_to_q(v, a):
	return Quaternion(np.append(
		v/np.linalg.norm(v) * np.sin(a/2),
		np.cos(a/2)
	))
