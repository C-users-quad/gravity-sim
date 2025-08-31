#version 330 core

layout(location = 0) in vec2 aPos;
layout(location = 1) in vec2 center;
layout(location = 2) in vec2 velocity;
layout(location = 3) in float radius;
layout(location = 4) in vec3 color;

uniform float u_WindowWidth;
uniform float u_WindowHeight;

out vec2 fragPos;
out vec3 particleColor;
out float fragRadius;

void main() 
{
    vec2 scaled = aPos * radius * 2.0;
    vec2 worldPos = scaled + center;
    vec2 ndc = (worldPos / vec2(u_WindowWidth, u_WindowHeight)) * 2.0 - 1.0;
    gl_Position = vec4(ndc, 0.0, 1.0);
    particleColor = color;
    fragPos = scaled;
    fragRadius = radius;
}