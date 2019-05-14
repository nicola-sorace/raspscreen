emulate = True

if emulate:
    import pygame as pg
    binds = {"up":pg.K_UP, "down":pg.K_DOWN, "left":pg.K_LEFT, "right":pg.K_RIGHT, "ok":pg.K_RETURN}
else:
    import RPi.GPIO as IO
    IO.setmode(IO.BOARD)  # Physical pin numbering
    binds = {"up":11, "ok":13, "down":15, "left":12, "right":16}
    for k in binds: IO.setup(k, IO.IN, pull_up_down=IO.PUD_DOWN)

down = {}  # Is key down
for k in binds: down[k] = False
clicked = down.copy()  # Is key just clicked
false_template = down.copy()  # Holds "False" array for clearing

def get_state():

    clicked = false_template.copy()

    if emulate:
        for event in pg.event.get():
            for name,key in binds.items():
                if event.type in [pg.KEYDOWN, pg.KEYUP] and event.key == key:
                    new_state = (event.type==pg.KEYDOWN)
                    clicked[name] = new_state and not down[name]
                    down[name] = new_state
    else:
        for name,key in binds.items():
            new_state = (IO.input(key)==IO.HIGH)
            clicked[name] = new_state and not down[name]
            down[name] = new_state

    return (down,clicked)
