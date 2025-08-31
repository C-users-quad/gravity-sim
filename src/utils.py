from settings import *

def resize_viewport(width, height, shader_program):
    glViewport(0, 0, width, height) # sets the size of opengls window.
    loc_w = glGetUniformLocation(shader_program, "u_WindowWidth")
    loc_h = glGetUniformLocation(shader_program, "u_WindowHeight")
    glUniform1f(loc_w, width)
    glUniform1f(loc_h, height)
    # glMatrixMode(GL_PROJECTION) # tells opengl we modifying the projection matrix.
    # glLoadIdentity() # sets the matrix to the identity matrix (its like the default).
    # glOrtho(0, width, height, 0, -1, 1) # switch gl coord system to pygame coord system.
    # glMatrixMode(GL_MODELVIEW) # switch to modelview modifications.
    # glLoadIdentity() # resets the modelview matrix, prevents affecting the next draw with old image transforms.

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