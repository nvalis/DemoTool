#version 450

layout(points) in;
layout(triangle_strip, max_vertices=4) out;

out gl_PerVertex { vec4 gl_Position; }; // might be needed

// Fullscreen Quad
// from http://stackoverflow.com/a/9343057

void main() {
	gl_Position = vec4(1., 1., 0., 1.);
	EmitVertex();

	gl_Position = vec4(-1., 1., 0., 1.);
	EmitVertex();

	gl_Position = vec4(1., -1., 0., 1.);
	EmitVertex();

	gl_Position = vec4(-1., -1., 0., 1.);
	EmitVertex();

	EndPrimitive();
}
