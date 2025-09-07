vertex_shader = (
    """
    attribute vec3 a_color;
    attribute vec2 a_pos;
    attribute float a_radius;

    uniform float u_HALF_WORLD_LENGTH;
    uniform vec2 u_CamPos;
    uniform float u_CamZoom;

    varying vec3 v_color;

    void main() {
        // sets world coords of particle point relative to the camera
        vec2 cam_relative = (a_pos - u_CamPos) * u_CamZoom;

        // transforms point pos in cam-relative world coords to opengl coords with +y going down.
        vec2 ndc = vec2(cam_relative.x / u_HALF_WORLD_LENGTH, -cam_relative.y / u_HALF_WORLD_LENGTH);

        // sets the position of the particle in opengl
        gl_Position  = vec4(ndc, 0.0, 1.0);

        // sets the diameter of the particle
        gl_PointSize = a_radius * u_CamZoom * 2;

        // sets the vertex color to the color passed in
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