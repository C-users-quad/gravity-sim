#version 330 core

layout(location = 0) in vec2 aPos;
layout(location = 1) in vec2 center;
layout(location = 2) in float radius;
layout(location = 3) in vec3 color;

uniform float u_WindowWidth;
uniform float u_WindowHeight;
uniform float u_CamZoom;
uniform vec2 u_CamPos;

out vec2 fragPos;
out vec3 particleColor;
out float fragRadius;

void main() 
{
    vec2 w_centerOffset = vec2(u_WindowWidth / 2, u_WindowHeight / 2);
    vec2 camRelativeCenter = (center - u_CamPos) * u_CamZoom;
    vec2 scaled = aPos * radius * u_CamZoom * 2.0;
    vec2 worldPos = camRelativeCenter + scaled + w_centerOffset;
    vec2 ndc = vec2(
        worldPos.x / u_WindowWidth * 2.0 - 1.0,
        1.0 - worldPos.y / u_WindowHeight * 2.0
    );
    gl_Position = vec4(ndc, 0.0, 1.0);
    particleColor = color;
    fragPos = scaled;
    fragRadius = radius * u_CamZoom;
}