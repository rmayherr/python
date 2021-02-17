#!/usr/bin/python3
import os, sys

class Example:
  """ Test python script """	
  def __init__(self,name,age):
    self.name=name
    self.age=age
  def write_out(self):
    print("Hello " + self.name + ".Your age is " + str(self.age))


if __name__ == "__main__":
  a=Example("Frank",32)
  a.write_out()
  print(sys.path)

