# -*- coding: utf-8 -*-
#! /usr/bin/python
from turtle import *
import random
title("Marking an area")
setup(500, 500, 0, 0)
bgcolor("orange")

delay(0)

for x in range(1,200):
    xpos = random.randint(-250,250)
    ypos = random.randint(-250,250)
    goto(xpos,ypos)
    dot(20,"blue")
done()
