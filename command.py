#!/usr/bin/python
import commands

cmd = "ls -l"
a = commands.getstatusoutput(cmd)
print a
