#TODO:
# -Persistent state + background function

from . import core

import time
from math import floor

class Timer(core.View):
    from . import menus

    title = "Timer"
    start_time = 0
    cur_time = start_time
    paused = True

    last = menus.Utility_Menu 
    
    def draw(self, g, font):
        if not self.paused: self.cur_time = time.time()
        diff = self.cur_time-self.start_time
        g.text((40,25), time.strftime("%H:%M:%S", time.gmtime(diff)), fill="white")
        g.line((40, 40, 40+50*(diff-floor(diff)), 40), fill="white")


    def parse_inputs(self, state):
        super().parse_inputs(state)

        if self.clicked["ok"]:
            if self.paused: self.start_time = time.time() - self.cur_time + self.start_time
            self.paused = not self.paused
        elif self.clicked["right"] and self.paused: self.start_time = self.cur_time

