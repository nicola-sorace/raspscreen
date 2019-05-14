import subprocess
import threading
import inspect

class View:
    
    title = "???"

    def __init__(self, main, last=None):
        self.main = main
        self.last = last

    def on_open(self):
        pass
    
    def draw(self, g, font):
        g.ellipse( (10,10,20,20) )

    def parse_inputs(self, state):
        (self.down, self.clicked) = state
        if self.last!=None and self.clicked["left"]: self.set_view(self.last)

    def set_view(self, C, **args):
        if inspect.isclass(C):
            if 'last' in args: C = C(self.main, **args)
            else: C = C(self.main, self, **args)
        self.main.set_view( C )
        C.on_open()

    def cmd(self, s):
        print(s)
        out = subprocess.Popen(s, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        line_iterator = iter(out.stdout.readline, b'')
        return (line_iterator, out)

class Menu(View):
    items = ["Item 1", "Item 2", "Item 3"]
    selected = 0
    offset = 0

    def draw(self, g, font):
        for i,n in list(enumerate(self.items))[self.offset:self.offset+4]:
            y = 12*(i-self.offset) + 14
            if i == self.selected:
                #g.line((0,y+6,5,y+6), fill="white")
                #g.text((14,y), n, font=font, fill="white")
                g.rectangle((0,y+2,120,y+12), fill="white")
                g.text((6,y), n, font=font, fill="black")
            else:
                g.text((2,y), n, font=font, fill="white")

        if len(self.items)>4:
            g.rectangle((124,16,127,63), outline="white")
            #a = 14+63*(1-(self.offset+4)/len(self.items))
            a = 16+63*((self.offset)/len(self.items))
            b = 63*((self.offset+4)/len(self.items))
            g.rectangle((124,a,127,b), fill="white")

    def parse_inputs(self, state):
        super().parse_inputs(state)

        if self.clicked["up"]: self.selected -= 1
        elif self.clicked["down"]: self.selected += 1
        if self.selected < 0: self.selected = len(self.items)-1
        elif self.selected > len(self.items)-1: self.selected = 0

        if self.selected < self.offset: self.offset = self.selected
        elif self.selected > self.offset+3: self.offset = self.selected-3

        if self.clicked["ok"] or self.clicked["right"]: self.run(self.selected)

    def run(self, n):
        if self.last!=None and self.items[n]==" <-": self.set_view(self.last)

class Input_View(View):

    alphs = [
                [chr(i) for i in range(97,123)], # Lowercase
                [chr(i) for i in range(65,91)],  # Uppercase
                [chr(i) for i in range(48,58)],  # Numbers
                [chr(i) for i in range(58,65)],  # Symbols 1
                [chr(i) for i in range(32,48)],  # Symbols 2
                [chr(i) for i in range(91,97)],  # Symbols 3
                [chr(i) for i in range(123,127)]  # Symbols 4
            ]

    def __init__(self, main, last, name, ref):
        self.title = name
        super().__init__(main, last)
        # 'ref' should be list containing only string to be edited
        self.ref = ref
        self.string = list(ref[0])
        
        self.editing = True
        self.char = 0
        self.anum = 0
        self.set_pos(0)

    def set_alph(self, anum):
        if anum<0: anum = len(alphs)-1
        elif anum>len(self.alphs)-1: anum = 0
        self.anum = anum
        self.alph = self.alphs[anum]
        self.set_char(self.char)
    
    def set_pos(self, pos):
        if pos<0 or pos>len(self.string):
            self.editing = False
            return
        self.pos = pos
        if pos<len(self.string):
            c = self.string[pos]
            for anum, alph in enumerate(self.alphs):
                if c in alph:
                    self.anum = anum
                    self.alph = alph
                    break
            self.char = self.alph.index(c)

    def set_char(self, char):
        if self.pos>len(self.string)-1:
            self.alph = self.alphs[0]
            self.string.append(self.alph[0])
            self.char = 0
        else:
            if char<0: char = len(self.alph)-1
            elif char>len(self.alph)-1: char = 0
            self.char = char
        self.string[self.pos] = self.alph[self.char]

    def parse_inputs(self, state):
        # Do not inherit super method
        (self.down, self.clicked) = state

        if self.editing:
            if self.clicked["left"]: self.set_pos(self.pos-1)
            elif self.clicked["right"]: self.set_pos(self.pos+1)
            elif self.clicked["up"]: self.set_char(self.char-1)
            elif self.clicked["down"]: self.set_char(self.char+1)
            elif self.clicked["ok"]: self.set_alph(self.anum+1)
        else:
            if self.clicked["up"]: self.editing = True
            elif self.clicked["left"]: self.set_view(self.last)
            elif self.clicked["ok"] or self.clicked["right"]:
                self.ref[0] = "".join(self.string)
                self.set_view(self.last)

    def draw(self, g, font):
        #g.text((0,14), self.name+":", font=font, fill="white")
        g.rectangle((0,30,127,45), outline="white")
        g.text((2,30), "".join(self.string), font=font, fill="white")
        if self.editing:
            g.line((2+self.pos*7.3,43,8+self.pos*7.4,43), fill="white")

class CMD_View(View):

    def __init__(self, main, last, s):
        self.title = s
        super().__init__(main, last)
        self.s = s

        self.font = self.main.make_font("Lucida Console.ttf", 9)
        #self.font = self.main.make_font("UbuntuMono-Regular.ttf", 10)
        self.lines = []
        self.offset = 0
        self.thread = None
        self.shell_proc = None
        
        self.thread = threading.Thread(target=self.track_lines)
        self.thread.start()
    
    def parse_inputs(self, state):
        super().parse_inputs(state)

        if self.clicked["up"] and self.offset<len(self.lines)-5: self.offset += 1
        elif self.clicked["down"] and self.offset>0: self.offset -= 1

    def set_view(self, C, **args):
        self.shell_proc.kill()
        self.thread.join()
        super().set_view(C, **args)

    def track_lines(self):
        (line_iterator, self.shell_proc) = self.cmd(self.s)
        for l in line_iterator:
            self.lines.append(l.decode("utf-8"))
        self.lines.append(" -------< EOF >-------")

    def draw(self, g, font):
        for i,l in enumerate(self.lines[-5-self.offset:len(self.lines)-self.offset]):
            g.text((0,14+9*i), l, font=self.font, fill="white")

        if len(self.lines)>5:
            g.rectangle((124,16,127,63), fill="black", outline="white")
            a = 16+63*(1-(self.offset+5)/len(self.lines))
            b = 63*(1-(self.offset)/len(self.lines))
            g.rectangle((124,a,127,b), fill="white")


