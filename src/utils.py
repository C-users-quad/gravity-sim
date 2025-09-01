from settings import *

def resize_viewport(width, height, shader_program):
    glViewport(0, 0, width, height) # sets the size of opengls window.
    
def pass_in_uniforms(shader_program, win_w, win_h, cam_zoom, cam_pos):
    loc_w = glGetUniformLocation(shader_program, "u_WindowWidth")
    loc_h = glGetUniformLocation(shader_program, "u_WindowHeight")
    loc_z = glGetUniformLocation(shader_program, "u_CamZoom")
    loc_p = glGetUniformLocation(shader_program, "u_CamPos")
    
    glUniform1f(loc_w, win_w)
    glUniform1f(loc_h, win_h)
    glUniform1f(loc_z, cam_zoom)
    glUniform2fv(loc_p, 1, cam_pos)

def get_shader_program(vertex_shader_path, frag_shader_path):
    with open(vertex_shader_path, 'r') as f:
        vertex_src = f.read()

    with open(frag_shader_path, 'r') as f:
        frag_src = f.read()

    shader_program = compileProgram(
        compileShader(vertex_src, GL_VERTEX_SHADER),
        compileShader(frag_src, GL_FRAGMENT_SHADER)
    )

    return shader_program