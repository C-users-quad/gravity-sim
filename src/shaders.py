vertex_shader = (
    """
    attribute vec3 a_color;
    attribute vec2 a_pos;
    attribute float a_radius;

    uniform float u_HALF_WORLD_LENGTH;
    uniform vec2 u_CamPos;
    uniform float u_CamZoom;

    varying vec3 v_color;

    void main() 
    {
        // compute world position relative to camera
        vec2 world_relative = a_pos - u_CamPos;

        // map to NDC [-1, 1] using zoom
        vec2 ndc = world_relative / (u_HALF_WORLD_LENGTH / u_CamZoom);

        // flip y if needed (OpenGL convention)
        ndc.y = -ndc.y;

        gl_Position = vec4(ndc, 0.0, 1.0);

        // scale point size with zoom
        gl_PointSize = a_radius * u_CamZoom * 2.0;

        v_color = a_color;
    }
    """
)

fragment_shader = (
    """
    varying vec3 v_color;

    void main() {
        vec2 coord = gl_PointCoord - vec2(0.5);
        float dist2 = dot(coord, coord);

        if (dist2 > 0.25) { // 0.5^2 = 0.25
            discard;
        }
         // sets the color of the fragment
        gl_FragColor = vec4(v_color, 1.0);
    }
    """
)