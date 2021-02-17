#!/usr/bin/env python3
import time, subprocess,os

class Progressbar():
    def __init__(self):
        self.line = ""
        self.arrow = ""
        self.initbar()

    def initbar(self):
        print(("{0:143}{1}").format("[","]"))

    def terminal_length(self):
        cols,rows = os.get_terminal_size()
        return cols

    def update(self):
        self.line += "="
        self.arrow = ">"
        print("{0}{1}{2:{l}}{3}".format("[", self.line, self.arrow, "]",l = 140 - len(self.line)))

bar = Progressbar()

for i in range(1,140):
    subprocess.call(["clear"])
#    print(i)
    bar.update()
    time.sleep(0.02)
