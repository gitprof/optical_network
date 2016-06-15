#!/bin/python

import imp
import os
import inspect

def xprint(msg):
    print(msg)

def test1():
    xprint('\n---Test1---')


if "__main__" == __name__:
    #path = os.path.splitdrive(me)
    print (inspect.getfile(inspect.currentframe()))
    print (os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
    test1()
    
