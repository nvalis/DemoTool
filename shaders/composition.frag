#version 450

in vec4 gl_FragCoord;
out vec4 FragColor;

uniform float time;
uniform vec2 resolution;

#define W 0.6
#define phi (1.+sqrt(5.))/2.

bool h_line(vec2 p, float y) {
	return abs(p.y - y) < W;
}

bool v_line(vec2 p, float x) {
	return abs(p.x - x) < W;
}

void main(void) {
	vec2 uv = gl_FragCoord.xy;
	vec4  third_color = vec4(.8,.2,.2, .4);
	vec4 golden_color = vec4(.8,.8,.2, .4);
	vec4 color = vec4(0.);

	// thirds
	if (h_line(uv, resolution.y*1./3.) || h_line(uv, resolution.y*2./3.)) {
		color = third_color;
	}
	if (v_line(uv, resolution.x*1./3.) || v_line(uv, resolution.x*2./3.)) {
		color = third_color;
	}

	// golden mean
	if (h_line(uv, resolution.y*1./(1.+phi)) || h_line(uv, resolution.y*phi/(1.+phi))) {
		color = golden_color;
	}
	if (v_line(uv, resolution.x*1./(1.+phi)) || v_line(uv, resolution.x*phi/(1.+phi))) {
		color = golden_color;
	}

	FragColor = color;
}