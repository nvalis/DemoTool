#version 450

in vec4 gl_FragCoord;
out vec4 fragColor;

uniform vec2 resolution;

void main() {
	vec2 uv = (2.*gl_FragCoord.xy - resolution.xy)/resolution.xy;
	fragColor = vec4(uv.xy,0, 1);
}