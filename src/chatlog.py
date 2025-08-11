from settings import *


class LogText(pygame.sprite.Sprite):
    """
    Used for displaying informational text to the player.
    Also functions as a sort of error log.
    """
    def __init__(self, text, font, groups, logtext, type="normal"):
        """
        Initialize a LogText sprite for displaying messages in the chat window.
        Args:
            text (str): The message to display.
            font (pygame.font.Font): Font used for rendering text.
            groups (iterable): Sprite groups to add this sprite to.
            logtext (list): List of all LogText objects for positioning.
            type (str): Type of message ('normal', 'error').
        """
        # display dimensions
        self.update_win_size_vars()

        # color setting
        color = self.text_color(type)

        # padding and spacing
        self.padding = 4 # horizontal spacing
        self.spacing = 2 # vertical spacing

        # initializes pygame.sprite.Sprite.__init__()
        super().__init__(groups)
        self.original_image = font.render(text, True, color).convert_alpha()
        self.image = font.render(text, True, color).convert_alpha()
        self.rect = self.image.get_frect(bottomleft = (self.padding, self.spacing))

        # dimensions. max width represents the maximum line width.
        self.width = self.image.get_width()
        self.height = self.image.get_height()

        # values relevant to fading
        self.alpha = 255
        self.fade_speed = 100
        self.fade_start = 2000
        self.time_of_birth = pygame.time.get_ticks()

        # all the other log texts
        self.logtext = logtext

    def text_color(self, type):
        """
        Get the color for the text based on its type.
        Args:
            type (str): The type of message ('normal', 'error').
        Returns:
            str: Color name for rendering.
        """
        if type.lower() == "error":
            return "red"
        elif type.lower() == "info":
            return "chartreuse"
        elif type.lower() == "hint":
            return "darkgoldenrod1"
        else:
            return "white"

    def fade(self, dt):
        """
        Fade out the text gradually after a set time.
        Kills the sprite when fully transparent.
        """
        current_time = pygame.time.get_ticks()
        if current_time - self.time_of_birth <= self.fade_start:
            return
        self.alpha -= self.fade_speed * dt
        if self.alpha <= 0:
            self.kill()
        else:
            self.image.set_alpha(self.alpha)

    def update_win_size_vars(self):
        self.win_w, self.win_h = pygame.display.get_surface().get_size()

    def update_position(self):
        """
        Adjust the position of the text to avoid overlap with other log messages.
        """
        # initially, the text is self.spacing above self.win_h so we set y_offset to this.
        y_offset = self.spacing
        # increments y offset by the height of the other texts below it
        for text in sorted(self.logtext, key = lambda text: text.time_of_birth, reverse = True):
            if text is self:
                break
            y_offset += text.height + self.spacing
        self.rect.bottomleft = (self.padding, self.win_h - y_offset)

    def killcheck(self):
        if self.rect.bottom <= 0:
            self.kill()

    def update(self, dt):
        """
        Update the sprite each frame: fade out and reposition.
        Deletes the sprite if its not in the bounds of the window.
        """
        self.killcheck()
        self.update_win_size_vars()
        self.fade(dt)
        self.update_position()
