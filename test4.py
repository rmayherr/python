#!/usr/bin/env python3
import math, sys

class Example:
    """ Test python script """
    def __init__(self,name,age):
        self.__name=name
        self.__age=age
    def write_out(self):
        try:
            assert self.__name == "", "Name is not known."
            assert self.__age == "", "Age is not known."
            print("Hello " + self.__name + ".Your age is " + str(self.__age))
        except AssertionError:
            print("Name or age is empty.")
            sys.exit(1)
    def __repr__(self):
        return repr('{0} {1}'.format(self.__name,self.__age))
    def __str__(self):
        return '%s, %s' % (self.__name,self.__age)
    @property
    def name(self):
        return self.__name
    @property
    def age(self):
        return self.__age
    @name.setter
    def name(self,name):
        self.__name = name
    @age.setter
    def age(self,age):
        self.__age = age
    @name.deleter
    def name(self):
        del self.__name
    @age.deleter
    def age(self):
        del self.__age
class Point:
    def __init__(self,x,y):
        self.x = x
        self.y = y
    def __repr__(self):
        return repr('x = {0}, y = {1}'.format(self.x,self.y))
    def base(self):
        print("From Point")
class Circle(Point):
    def __init__(self,radius,x,y):
        super().__init__(x,y)
        self.radius = radius
    def area(self):
        return "{0:6.2f}".format(math.pi * (self.radius ** 2))
    def base(self):
        print("Form Circle")
    def base2(self):
        super().base()
if __name__ == "__main__":
    a=Example("Frank",32)
    a.write_out()
    a.name = "Joe"
    a.age = 12
    a.write_out()
    del a.name
    del a.age
    a.write_out()

#    repr(a)
#    print(repr(a))
#    print(str(a))
#    c = Circle(20,12,45)
#    print(c.area())
#    c.base()
#    c.base2()
