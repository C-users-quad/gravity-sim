vertex_shader = (
    """
    attribute vec3 a_color;
    attribute vec2 a_pos;
    attribute float a_radius;

    uniform vec2 u_CamPos;
    uniform float u_CamZoom;
    uniform vec2 u_WindowSize;

    varying vec3 v_color;

    void main()
    {
        // Camera-relative world position
        vec2 cam_relative = a_pos - u_CamPos;

        // Scale by zoom (world units -> pixels)
        vec2 pos_pixels = cam_relative * u_CamZoom;

        // Convert to NDC
        vec2 ndc = pos_pixels / (u_WindowSize / 2.0);

        gl_Position = vec4(ndc, 0.0, 1.0);

        // Point size in pixels
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