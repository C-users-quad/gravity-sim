#version 330 core

in vec2 fragPos;
in vec3 particleColor;
in float fragRadius;

out vec4 FragColor;

void main() 
{
    // discard fragments outside the circle
    if (length(fragPos) > fragRadius) {
        discard;
    }

    FragColor = vec4(particleColor, 1.0);
}