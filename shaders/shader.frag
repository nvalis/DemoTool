#version 450

in vec4 gl_FragCoord;
out vec4 FragColor;

uniform float time;
uniform vec2 resolution;

uniform vec3 camera_position;
uniform mat3 camera_rotation;

#define EPS 1e-4

// http://byteblacksmith.com/improvements-to-the-canonical-one-liner-glsl-rand-for-opengl-es-2-0/
highp float rand(vec2 co) {
	float dt = dot(co.xy,vec2(12.9898,78.233));
	return fract(sin(mod(dt,3.1416))*43758.5453);
}

mat3 camera(vec3 f, vec3 u) {
	return mat3(normalize(cross(f,u)), u, -f);
}

float sdSphere(vec3 p, float s) {
	return length(p)-s;
}

float sdBox(vec3 p, vec3 b) {
	vec3 d = abs(p) - b;
	return min(max(d.x,max(d.y,d.z)),0.)+length(max(d,0.));
}

float refd = 9e99;
float refrd = 9e99;
float scene(vec3 p){
	refd = sdSphere(p, .5);
	refrd = sdSphere(p+vec3(.6,.4,.4), .1);
	return min(min(refd,refrd), -sdBox(p+vec3(2.,-1.5,-3.5), vec3(4.,2.,4.)));
}

vec3 normal(vec3 p) {
	vec2 e = vec2(EPS, 0.);
	float d = scene(p);
	return normalize(vec3(scene(p+e.xyy)-d, scene(p+e.yxy)-d, scene(p+e.yyx)-d));
}

float calcAO(vec3 p, vec3 n) {
	float occ = 0., sca = 1.;
	for (int i=0; i<5; i++) {
		float hr = .01 + .12*float(i)/4.;
		vec3 aopos = p + n * hr;
		float d = scene(aopos);
		occ += -(d-hr)*sca;
		sca *= .95;
	}
	return clamp(1.-3.*occ, 0., 1.);
}

vec3 lighting(vec3 p, vec3 lightPos) {
	vec3 lightCol = vec3(1.,.95,.95);
	float lightInt = 2.;
	vec3 diffuseCol = vec3(1.);
	float ambientInt = 0.04;
	vec3 ambientCol = vec3(1.);
	
	float wl = 0.0;
	if (p.x > -0.7) {
		if (fract(3.*p.y+time) < 0.19) {
			if (p.z < -.5+EPS || p.x > 2.-EPS || p.y < -.5+EPS) {
				wl = 10.;
			}
		}
	} else {
		if (fract(1.5*p.y+time+1.3) < 0.105) {
			if (p.z < -.5+EPS || p.x > 2.-EPS || p.y < -.5+EPS) {
				wl = 10.;
			}
		}
	}
	
	vec3 n = normal(p);
	float ao = calcAO(p, n);
	vec3 lightDir = normalize(lightPos-p);
	vec3 color = lightInt*vec3(max(dot(lightDir,n), 0.))*lightCol/pow(distance(p, lightPos), 2.)*diffuseCol*ao + ambientCol*ambientInt*ao + wl;
	
	return color;
}

void raytrace(vec3 ro, vec3 rd, out vec3 p) {
	p = ro;
	float d; vec3 n;
	for (int i=0; i<256; i++) { 
		p += rd*(d=scene(p));
		if (abs(d)<EPS) {
			if (d==refd) {
				p += EPS*(n=normal(p));
				rd = reflect(rd, n);
			} else if (d==refrd) {
				p += EPS*rd;
				n = normal(p);
				if (d > 0.) rd = refract(rd, n, 1./1.52);
				else rd = refract(rd, n, 1.52);
				p += EPS*rd;
			}
			else break;
		}
	}
}

void main(void) {
	vec2 uv = (2.*gl_FragCoord.xy-resolution.xy)/max(resolution.x,resolution.y);

	vec3 lp = vec3(-2.,3.5,3.5);
	//vec3 ro = vec3(-1.5-.2*sin(time),-.2+.2*cos(time),1.+.8*cos(time));
	vec3 ro = vec3(-1.65,-.04,.75);

	// camera setup
	mat3 c = camera(vec3(0.,0.,-1.), vec3(0.,1.,0.));
	vec3 rd = c*normalize(vec3(uv.xy, -1.));

	// camera control
	ro += camera_position;
	rd *= camera_rotation;

	vec3 color;
	vec3 p;
	raytrace(ro,rd, p);
	color = lighting(p, lp);

	float vignette = smoothstep(2.0, 2.0-0.45, length(uv));
	color = mix(color, color*vignette, 0.3);
	
	FragColor = vec4((pow(color, vec3(1./1.3))+0.04*rand(3.*uv)), 1.);
}