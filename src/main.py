from settings import *

class Game:
    def __init__(self):
        pygame.init()
        self.display = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), 
                                               pygame.OPENGL | pygame.DOUBLEBUF
                                            )
        self.clock = pygame.time.Clock()
        glClearColor(0.0, 0.0, 0.0, 1) # (RGBA) tuple. setter for the color stored in GL_COLOR_BUFFER_BIT.
        self.shader = self.create_shader(
            join('shaders', 'vertex.txt'), 
            join('shaders', 'fragment_shader.txt')
        )
        glUseProgram(self.shader) # its just a good idea to have a shader in use before creating an object that uses it.
        self.triangle = Triangle()
        self.on = True
        self.run()

    def create_shader(self, vertex_file_path, fragment_file_path):
        # reads the vertex and fragment shader files and creates a variable that holds their data as a string.
        with open(vertex_file_path, 'r') as file:
            vertex_src = file.readlines()

        with open(fragment_file_path, 'r') as file:
            fragment_src = file.readlines()

        shader = compileProgram(
            # compile shader takes in the source code of the shader (what it does), and a constant that tells opengl what kind of shader it is.
            compileShader(vertex_src, GL_VERTEX_SHADER),
            compileShader(fragment_src, GL_FRAGMENT_SHADER)
        )

        return shader

    def run(self):
        while self.on:
            dt = self.clock.tick(FPS) / 1000

            self.event_handler()

            # screen refresh.
            glClear(GL_COLOR_BUFFER_BIT) # fills the screen with the color as set in glClearColor() in the game constructor.

            # draw a triangle.
            glUseProgram(self.shader)
            glBindVertexArray(self.triangle.vao)
            glDrawArrays(GL_TRIANGLES, 0, self.triangle.vertex_count)

            pygame.display.flip()
        self.quit()

    def quit(self):
        self.triangle.destroy()
        glDeleteProgram(self.shader)
        pygame.quit()
        sys.exit()

    def event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.on = False

class Triangle:
    def __init__(self):
        """
        Creates the triangle.
        """
        # x, y, z, r, g, b
        # each row is a vertex that contains a position(xyz) and a color.(rgb)
        # in this case, z will be zero because i want this to be 2d.
        self.vertices = (
            -0.5, -0.5, 0.0, 1.0, 0.0, 0.0,
             0.5, -0.5, 0.0, 0.0, 1.0, 0.0, 
             0.0,  0.5, 0.0, 0.0, 0.0, 1.0
        )
        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.vertex_count = 3
        bytes_in_f32 = np.dtype(np.float32).itemsize

        # generates a vao id
        self.vao = glGenVertexArrays(1)
        # tells opengl to use the vao id
        glBindVertexArray(self.vao)

        # Generates one buffer object id. self.vbo now contains that id.
        self.vbo = glGenBuffers(1)
        # Binds the buffer GL_ARRAY_BUFFER to the id vbo. also just tells opengl to use the vbo buffer id.
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        # allocates gpu memory for gl array buffer. also fills that memory with self.vertices.
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        # use attrib 0 for position with 3 indices that are floats, and prenormalized. 
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, bytes_in_f32*6, ctypes.c_void_p(0))
        # use attrib 1 for color with 3 indices that are floats, and prenormalized.
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, bytes_in_f32*6, ctypes.c_void_p(bytes_in_f32*3))
        
    def destroy(self):
        """
        Free the memory when exitting the program.
        """
        # these 2 functions expect lists, so we give them a list, even if it has one item (self.vao/vbo.)
        # we add this little comma at the end to signify that the parenthasees arent for math but for a list.
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))

if __name__ == "__main__":
     game = Game()
