#!/usr/bin/env python3
import time, subprocess,os

class Progressbar():

    def __init__(self):
        self.stopped = 0
        self.bar_array = ['-','\\','|','/']
        self.current_item = 0

    def update(self):
        subprocess.call(["clear"])
        print(self.bar_array[self.current_item])
        if self.current_item == len(self.bar_array) - 1:
            self.current_item = 0
        else:
            self.current_item = self.current_item + 1
    def start(self):
        while True:
            if self.stopped == 1:
                break
            else:
                self.update()
                time.sleep(0.2)
    def stop(self):
        self.stopped = 1

if __name__ == '__main__':
    bar = Progressbar()
    bar.start()

