import os
import time
import _thread
from demo_opts import get_device
from luma.core.render import canvas
from PIL import ImageFont

from GUI import core, menus
import Input

class Main:
    def __init__(self):
        self.font = self.make_font("RobotoMono-Regular.ttf", 12)
        #self.font = self.make_font("Lucida Console.ttf", 12)
        self.view = menus.Main_Menu(self)

    def make_font(self, name, size):
        font_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), 'fonts', name))
        return ImageFont.truetype(font_path, size)

    def set_view(self, v):
        self.view = v

    def event_loop(self):
        while True: self.view.parse_inputs(Input.get_state())

    def draw_header(self, g):
        title = self.view.title
        g.text(( max(2,(128-len(title)*7.3)/2), 0), title, font=self.font, fill="white")
        #g.text((2,0), time.strftime("%Y/%m/%d  %H:%M"), font=self.font, fill="white")

    def draw(self, g):
        self.draw_header(g)
        self.view.draw(g, self.font)
        self.view.parse_inputs(Input.get_state())


main = Main()

if __name__ == "__main__":
    try:
        device = get_device()
        #_thread.start_new_thread(event_loop, ())
        while True:
            with canvas(device) as g:
                main.draw(g)

    except KeyboardInterrupt:
        print("Keyboard interrupt")
