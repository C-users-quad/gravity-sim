from settings import *


# testing if the shader works. output should be [2, 2]
# update code to match shader.
pygame.init()
aPos = pygame.Vector2(0.5, 0.5)
center = pygame.Vector2(1, 1)
radius = 1

scaled = aPos * radius * 2
worldPos = scaled + center
print(worldPos)
