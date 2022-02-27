#!/usr/bin/python
from micropi import IRDetect

ir = IRDetect()

while True:
    key = ir.read()
    if key != None:
        print(key)
