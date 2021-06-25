# -*- coding: utf-8 -*-
"""
Created on Sat Jun 19 00:28:31 2021

@author: Benjamin
"""

class Parent_Class(object):

    def __init__(self):
        super(Parent_Class, self).__init__()

    def parent_method(self):
        print('This is a parent method')


class Child_Class(Parent_Class):

    def __init__(self):
        super(Child_Class, self).__init__()

    def child_method(self):
        # Because of super, self of child class is aware of all its parent's methods and properties.
        self.parent_method()