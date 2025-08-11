from settings import *
from utils import *

def display_hints(logprinter):
    time = pygame.time.get_ticks()
    # prints a hint every minute
    if time % 6000 != 0:
        return
    type = "hint"
    hints = [
        "You can refill the simulation with particles by pressing r!",
        "You CANT turn off hints. Cry about it until the next update where I implement this.",
        "Im not updating this ever, too lazy. (/j)",
        "You can stop tracking a particle's info by pressing escape!",
        "You can shower by standing up and turning the big handle in your bathroom.",
        "When you release a dragged particle, its launched in the direction and speed of the cursor just before you let go!",
        "You can delete a particle by selecting it with RMB and pressing backspace.",
        "Look away from your screen for a few seconds you gaming goblin! Dont lose your vision!"
    ]
    random_hint_index = randint(0, len(hints) - 1)
    logprinter.print(hints[random_hint_index], type="hint")
