from settings import *
from utils import *

def display_hints(font, logtext, particles, time):
    # prints a hint every minute
    if time % 6000 != 0:
        return
    type = "hint"
    hints = [
        "Hint: You can refill the simulation with particles by pressing r!",
        "Hint: You CANT turn off hints. Cry about it until the next update where I implement this.",
        "Hint: Im not updating this ever, too lazy. (/j)",
        "Hint: You can stop tracking a particle's info by pressing escape!",
        "Hint: You can shower by standing up and turning the handle.",
        "Hint: When you release a dragged particle, its launched in the direction and speed of the cursor just before you let go!",
        "Hint: You can delete a particle by selecting it with RMB and pressing backspace.",
        "Hint: Look away from your screen for a few seconds you gaming goblin! Dont lose your vision!"
    ]
    random_hint_index = randint(0, len(hints) - 1)
    print_to_log(hints[random_hint_index], font, logtext, logtext, type="hint")
