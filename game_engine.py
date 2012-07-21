# -*- coding: utf-8 -*-
"""
Created on Wed Jul 04 10:19:35 2012

@author: pmaurier
"""

class Engine:
    def __init__(self):
        
        #            - |  +
        #          432101234
        #      -4  ....#####
        #      -3  ...#oooo#
        #      -2  ..#ooooo#
        #      -1  .#oooooo#
        #       0  #ooo+ooo#
        #       1  #oooooo#.
        #       2  #ooooo#..
        #       3  #oooo#...
        #       4  #####....
        self.table = [[-1,-1,-1,-1, 0, 0, 0, 0, 0],
                      [-1,-1,-1, 0, 0, 0, 0, 0, 0],
                      [-1,-1, 0, 0, 0, 0, 0, 0, 0],
                      [-1, 0, 0, 0, 0, 0, 0, 0, 0],
                      [ 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [ 0, 0, 0, 0, 0, 0, 0, 0,-1],
                      [ 0, 0, 0, 0, 0, 0, 0,-1,-1],
                      [ 0, 0, 0, 0, 0, 0,-1,-1,-1],
                      [ 0, 0, 0, 0, 0,-1,-1,-1,-1]]
        self.range_x = range(-4,5)
        self.range_y = range(-4,5)
        self.valid_pos = []
        for x in self.range_x:
            for y in self.range_y:
                if self._get_item(x, y) != -1:
                    self.valid_pos.append((x, y))
        self.animate_dict = {}
        self.check_list = []
        self.colors = [1, 2, 3, 11, 12, 13, 21, 22, 23, 31, 32, 33, 41, 42, 43, 51, 52, 53, 61, 62, 63, 71, 72, 73, 81, 82, 83, 91, 92, 93]

    def next_color(self, color):
        num = self.colors.index(color)
        if len(self.colors) == (num + 1):
            return self.colors[0]
        else:
            return self.colors[num + 1]
    
    def push(self, x, y, direction):
        self.animate_dict[(x,y)] = ["push", 0, direction]

        if direction[0] == "r":
            if self._get_item(x+direction[1], y) != 0:
                self.push(x+direction[1], y, direction)
            self.set_item(x+direction[1], y, self._get_item(x, y))
            self.check_list.append((x+direction[1], y))
            self.set_item(x, y, 0)
        elif direction[0] == "g":
            if self._get_item(x, y+direction[1]) != 0:
                self.push(x, y+direction[1], direction)
            self.set_item(x, y+direction[1], self._get_item(x, y))
            self.check_list.append((x, y+direction[1]))
            self.set_item(x, y, 0)
        elif direction[0] == "b":
            if self._get_item(x+direction[1], y-direction[1]) != 0:
                self.push(x+direction[1], y-direction[1], direction)
            self.set_item(x+direction[1], y-direction[1], self._get_item(x, y))
            self.check_list.append((x+direction[1], y-direction[1]))
            self.set_item(x, y, 0)
        return True
    
    def explosions(self):
        combined_list = []
        for item in self.check_list:
            if self._get_item(*item) != 0:
                current = self._get_item(*item)
                if self.explode(*item):
                    self.set_item(item[0], item[1], self.next_color(current))
                    combined_list.append(item)
        return combined_list
    
    def explode(self, x, y):
        area = self._get_area(x, y)
        if len(area) >= 3:
            for item in area:
                self.explode_item(*item)
            return True
        return False
            
    def _get_neighbors(self, x, y):
        list_neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1), (x+1, y-1), (x-1, y+1)]
        return list(set(list_neighbors)&set(self.valid_pos))
    
    def _get_common_neighbors(self, x, y):
        list_common = [(x, y)]
        for neighbor in self._get_neighbors(x, y):
            if self._get_item(*neighbor) == self._get_item(x, y):
                list_common.append(neighbor)
        return list_common
        
    def _get_area(self, x, y):
        test_list = [(x, y)]
        tested_list = []
        while len(test_list) != 0:
            for neighbor in self._get_common_neighbors(*test_list[0]):
                if not(neighbor in tested_list+test_list):
                    test_list.append(neighbor)
            tested_list.append(test_list[0])
            test_list.pop(0)
        return tested_list
    
    def _get_item(self, x, y):
        return self.table[y + 4][x + 4]
        
    def set_item(self, x, y, value):
        old_value = self._get_item(x, y)
        self.table[y + 4][x + 4] = value
        return old_value
    
    def print_table(self):
        for row in self.table:
            line = ""
            for item in row:
                if item == -1:
                    line += "  "
                elif item == 0:
                    line += ".."
                else:
                    if len(str(item)) == 1:
                        line += " "+str(item)
                    else:
                        line += str(item)
            print line
    
    def is_border(self, x, y):
        if ((x in [-4, 4] or y in [-4, 4]) and abs(x+y) < 5) or (x + y) in [-4, 4]:
            return True
        else:
            return False
    
    def clean_borders(self):
        for x in self.range_x:
            for y in self.range_y:
                if self.is_border(x, y):
                    self.vanish_item(x, y)
    
    def vanish_item(self, x, y):
        self.animate_dict[(x,y)] = ["vanish", 0]
        self.set_item(x, y, 0)
    
    def explode_item(self, x, y):
        self.animate_dict[(x,y)] = ["explode", 0]
        self.set_item(x, y, 0)
    
    def create_item(self, x, y, value):
        self.animate_dict[(x,y)] = ["create", 0, value]
        self.set_item(x, y, value)
    
if __name__ == "__main__":
    engine = Engine()
    engine.set_item(0,-3,1)
    engine.set_item(1,-3,2)
    engine.set_item(0,-4,1)
    engine.set_item(-1,-2,2)
    engine.set_item(-1,-1,1)
    engine.print_table()
    engine.push(0, -4, ("g",1))
    engine.print_table()
    while engine.check_list:
        print engine.check_list
        engine.check_list = engine.explosions()
        engine.print_table()