from random import random
from time import clock
import sys

#Auxiliary functions for generating RLE:
def rlstr(i):
    if i == 1:
        return ""
    elif i == 0:
        return "Out of Range!"
    else:
        return str(i)
def rlint(s):
    if s == "":
        return 1
    else:
        return int(s)
#There's probably a better way to do this
def toBinary(n):
    return ''.join(str(1 & int(n) >> i) for i in range(9)[::-1])
#And this. I don't even think it's actually being used for the moment.
class Proxy:
    def __init__(self, grd):
        self.grid = grd

#Due to the use of bitwise operators in step(), non-totalistic rules actually run at least 10% faster than outer-totalistic rules.
class CellularAutomaton:
    notationdict = { 
                     "0e" : "0,0,0,0,0,0,0,0",
                     "1e" : "1,0,0,0,0,0,0,0",  #   N
                     "1c" : "0,1,0,0,0,0,0,0",  #   NE
                     "2a" : "1,1,0,0,0,0,0,0",  #   N,  NE
                     "2e" : "1,0,1,0,0,0,0,0",  #   N,  E
                     "2k" : "1,0,0,1,0,0,0,0",  #   N,  SE
                     "2i" : "1,0,0,0,1,0,0,0",  #   N,  S
                     "2c" : "0,1,0,1,0,0,0,0",  #   NE, SE
                     "2n" : "0,1,0,0,0,1,0,0",  #   NE, SW
                     "3a" : "1,1,1,0,0,0,0,0",  #   N,  NE, E
                     "3n" : "1,1,0,1,0,0,0,0",  #   N,  NE, SE
                     "3r" : "1,1,0,0,1,0,0,0",  #   N,  NE, S      (3r in non-swapped notation)
                     "3q" : "1,1,0,0,0,1,0,0",  #   N,  NE, SW
                     "3j" : "1,1,0,0,0,0,1,0",  #   N,  NE, W
                     "3i" : "1,1,0,0,0,0,0,1",  #   N,  NE, NW
                     "3e" : "1,0,1,0,1,0,0,0",  #   N,  E,  S
                     "3k" : "1,0,1,0,0,1,0,0",  #   N,  E,  SW
                     "3y" : "1,0,0,1,0,1,0,0",  #   N,  SE, SW     (3y in non-swapped notation)
                     "3c" : "0,1,0,1,0,1,0,0",  #   NE, SE, SW
                     "4a" : "1,1,1,1,0,0,0,0",  #   N,  NE, E,  SE
                     "4r" : "1,1,1,0,1,0,0,0",  #   N,  NE, E,  S  (4r in non-swapped notation)
                     "4q" : "1,1,1,0,0,1,0,0",  #   N,  NE, E,  SW
                     "4i" : "1,1,0,1,1,0,0,0",  #   N,  NE, SE, S
                     "4y" : "1,1,0,1,0,1,0,0",  #   N,  NE, SE, SW (4y in non-swapped notation)
                     "4k" : "1,1,0,1,0,0,1,0",  #   N,  NE, SE, W
                     "4n" : "1,1,0,1,0,0,0,1",  #   N,  NE, SE, NW
                     "4z" : "1,1,0,0,1,1,0,0",  #   N,  NE, S,  SW
                     "4j" : "1,1,0,0,1,0,1,0",  #   N,  NE, S,  W
                     "4t" : "1,1,0,0,1,0,0,1",  #   N,  NE, S,  NW
                     "4w" : "1,1,0,0,0,1,1,0",  #   N,  NE, SW, W
                     "4e" : "1,0,1,0,1,0,1,0",  #   N,  E,  S,  W
                     "4c" : "0,1,0,1,0,1,0,1",  #   NE, SE, SW, NW
                     "5a" : "0,0,0,1,1,1,1,1",  #   SE, S,  SW, W,  NW
                     "5n" : "0,0,1,0,1,1,1,1",  #   E,  S,  SW, W,  NW
                     "5r" : "0,0,1,1,0,1,1,1",  #   E,  SE, SW, W,  NW (5r in non-swapped notation)
                     "5q" : "0,0,1,1,1,0,1,1",  #   E,  SE, S,  W,  NW
                     "5j" : "0,0,1,1,1,1,0,1",  #   E,  SE, S,  SW, NW
                     "5i" : "0,0,1,1,1,1,1,0",  #   E,  SE, S,  SW, W
                     "5e" : "0,1,0,1,0,1,1,1",  #   NE, SE, SW, W,  NW,
                     "5k" : "0,1,0,1,1,0,1,1",  #   NE, SE, S,  W,  NW
                     "5y" : "0,1,1,0,1,0,1,1",  #   NE, E,  S,  W, NW  (5y in non-swapped notation)
                     "5c" : "1,0,1,0,1,0,1,1",  #   N,  E,  S,  W,  NW
                     "6a" : "0,0,1,1,1,1,1,1",  #   E,  SE, S,  SW, W,  NW
                     "6e" : "0,1,0,1,1,1,1,1",  #   NE, SE, S,  SW, W,  NW
                     "6k" : "0,1,1,0,1,1,1,1",  #   NE, E,  S,  SW, W,  NW
                     "6i" : "0,1,1,1,0,1,1,1",  #   NE, E,  SE, SW, W,  NW
                     "6c" : "1,0,1,0,1,1,1,1",  #   N,  E,  S,  SW, W,  NW
                     "6n" : "1,0,1,1,1,0,1,1",  #   N,  E,  SE, S,  W,  NW
                     "7e" : "0,1,1,1,1,1,1,1",  #   NE, E,  SE, S,  SW, W,  NW
                     "7c" : "1,0,1,1,1,1,1,1",  #   N,  E,  SE, S,  SW, W,  NW
                     "8e" : "1,1,1,1,1,1,1,1"
                    }
    #Supports 2-D Moore-neighborhood non-totalistic isotropic rules as well as arbitrary
    # dimensional/neighborhood outer-totalistic rules (albeit with limited support for
    # fancier stuff such as RLE and transformations).
    def __init__(self, dims = 3, nbhd = None, range_ = 1, rule = None, hensel = False):
        self.range_ = range_ #for copy()
        if hensel:
            self.hensel = True
            self.transitions = [[False for i in xrange(256)], [False for i in xrange(256)], [False for i in xrange(256)]]
            self.dims = 2
            self.nbhd = [(i,j) for i in xrange(3) for j in xrange(3)]
            #Cells are stored in self.grid as tuples representing position vectors
            self.grid = {}
            self.gen = 0
            self.t1 = 0
            self.t2 = 0
            self.t3 = 0
            self.rulestring = "B/S"
            if rule is not None:
                self.setrule(rule)
            return
        self.hensel = False
        if nbhd is None:
            nbhd = lambda *args:( reduce((lambda x, y: x+y), map((lambda x: abs(x**dims)), args)) < range_*dims)
        self.grid = {}
        self.dims = dims
        
        #Emulate recursion:
        q = [[]]
        for i in xrange(dims):
            q = [j + [k] for j in q for k in xrange(-range_, range_+1)]
        self.nbhd = [tuple(i) for i in q if nbhd(*i)]
        
        self.rule = ([False for i in self.nbhd], [False for i in self.nbhd])
        self._firstrule = len(self.nbhd)+1
        self.b = []
        self.s = []
        self.gen = 0
        self.t1 = 0
        self.t2 = 0
        self.t3 = 0
        if rule is not None:
            self.setrule(rule)
    
    def empty(self):
        return not len(self.grid)
    
    #Generates the neighborhood of a given cell (for use in step()).
    def genNB(self, cell):
        return [tuple([i[j] + cell[j] for j in xrange(self.dims)]) for i in self.nbhd]
    
    #Generates the next generation of the pattern as a whole.
    # (Heavily optimized manually, including visually obvious techniques such as loop unrolling.)
    def step(self):
        if self.empty():
            return
        if self.hensel:
            t = clock()
            tempgrid = {}
            tempgrid3 = {}
            qq = self.grid.keys()
            for j1, j2 in qq:
                tempgrid[(j1-1, j2+1)] = 0x1
            for j1, j2 in qq:
                q = (j1, j2+1)
                if q in tempgrid:
                    tempgrid[q] += 0x2
                else:
                    tempgrid[q] = 0x2
                q2 = (j1+1, j2+1)
                if q2 in tempgrid:
                    tempgrid[q2] += 0x4
                else:
                    tempgrid[q2] = 0x4
                q3 = (j1+1, j2)
                if q3 in tempgrid:
                    tempgrid[q3] += 0x8
                else:
                    tempgrid[q3] = 0x8
                q4 = (j1+1, j2-1)
                if q4 in tempgrid:
                    tempgrid[q4] += 0x10
                else:
                    tempgrid[q4] = 0x10
                q5 = (j1, j2-1)
                if q5 in tempgrid:
                    tempgrid[q5] += 0x20
                else:
                    tempgrid[q5] = 0x20
                q6 = (j1-1, j2-1)
                if q6 in tempgrid:
                    tempgrid[q6] += 0x40
                else:
                    tempgrid[q6] = 0x40
                q7 = (j1-1, j2)
                if q7 in tempgrid:
                    tempgrid[q7] += 0x80
                else:
                    tempgrid[q7] = 0x80
            t2 = clock()
            self.t1 += t2-t
            transitions = self.transitions
            grid = self.grid
            for i, ns in tempgrid.items():
                if not transitions[2][ns]:
                    continue
                if transitions[i in grid][ns]:
                    tempgrid3[i] = 0
            t = clock()
            self.t2 += t-t2
            self.grid = tempgrid3
            self.gen += 1
            t2 = clock()
            self.t3 += t2-t
            return
        t = clock()
        tempgrid = {}
        tempgrid3 = {}
        if self.dims == 2:
            for i1, i2 in self.nbhd:
                for j1, j2 in self.grid:
                    q = (j1+i1, j2+i2)
                    if q in tempgrid:
                        tempgrid[q] += 1
                    else:
                        tempgrid[q] = 1
        elif self.dims == 3:
            for i1, i2, i3 in self.nbhd:
                for j1, j2, j3 in self.grid:
                    q = (j1+i1, j2+i2, j3+i3)
                    if q in tempgrid:
                        tempgrid[q] += 1
                    else:
                        tempgrid[q] = 1
        elif self.dims == 1:
            for i, in self.nbhd:
                for j, in self.grid:
                    q = (j+i,)
                    if q in tempgrid:
                        tempgrid[q] += 1
                    else:
                        tempgrid[q] = 1
        else:
            for i in self.grid:
                for j in self.genNB(i):
                    if j in tempgrid:
                        tempgrid[j] += 1
                    else:
                        tempgrid[j] = 1
        t2 = clock()
        self.t1 += t2-t
        for i in tempgrid:
            nc = tempgrid[i]
            if nc < self._firstrule:
                continue
            state = i in self.grid
            if self.rule[state][nc-state]:
                tempgrid3[i] = 0
        t = clock()
        self.t2 += t-t2
        self.grid = tempgrid3
        self.gen += 1
        t2 = clock()
        self.t3 += t2-t
    
    #Most (but not all) of this non-totalistic handling code copied from @wildmyron's apgsearch-isotropic.py (if I'm remembering right; it was about 2-3 years ago that I wrote casim).
    def writetransition_0(self, center, code):
        code = int(self.notationdict[code].replace(",", ""), 2)
        codes = []
        for _ in xrange(4):
            if code not in codes:
                codes.append(code)
            temp = code >> 6
            code = ((code << 2) & 0xFF) | temp
        code = ((code & 0x55) << 1) | ((code & 0xAA) >> 1)
        code = ((code & 0x33) << 2) | ((code & 0xCC) >> 2)
        code = ((code & 0x0F) << 4) | ((code & 0xF0) >> 4)
        temp = code >> 7
        code = ((code << 1) & 0xFF) | temp
        for _ in xrange(4):
            if code not in codes:
                codes.append(code)
            temp = code >> 6
            code = ((code << 2) & 0xFF) | temp
        for i in codes:
            self.transitions[center == "1,"][i] = True
            self.transitions[2][i] = True
    def writetransition(self, bs, totalistic_num, notation_letter, inverse_list):
        ''''if totalistic_num == "0":
            self.transitions[bs == "1,"][0] = True
        elif totalistic_num == "8":
            self.transitions[bs == "1,"][255] = True
        el'''
        if notation_letter != "none":
            self.writetransition_0(bs, totalistic_num+notation_letter)
        elif inverse_list != []:
            for i in self.notationdict:
                if not (i[1] in inverse_list) and i.startswith(totalistic_num):
                    self.writetransition_0(bs, i)
        else:
            for i in self.notationdict:
                if i.startswith(totalistic_num):
                    self.writetransition_0(bs, i)
    def parseHensel(self, rulestring):
        self.transitions = [[False]*256, [False]*256, [False]*256]
        # The following code cleans up the rulestring
        # so that it makes a valid and somewhat readable file name - eg "B2-a_S12.table"
        
        rulestring = rulestring.replace(" ", "")
        rulestring = rulestring.lower()
        rulestring = rulestring.replace("b", "B")
        rulestring = rulestring.replace("s", "S")
        
        #  The following code cleans up the rule string to
        #  make life easier for the parser.
        
        if rulestring.startswith("B") or rulestring.startswith("S"):
            rulestring = rulestring.replace("/", "")
        else:
            rulestring = rulestring.replace("/", "B")
        #The following line is not related at all to the surrounding code:
        self.rulestring = rulestring.replace("S", "/S")
        
        rulestring = rulestring + "\n"
        # Parse the rulestring, and add transitions as we go.
        
        # Lets say rule strings contain "rule elements", such as B2i, or B2-a, which are composed of:
        # 1) a birth or survival flag
        # 2) a "totalistic context" consisting of an integer between zero and 8
        # 3) a "notation_letter".   
        # 4) a flag for "positive" or "inverse" notation
        
        bs = "1,"                        # Use "1," for survival or "0," for birth
        totalistic_context = "none"      # "none" will be replaced with "0" through
                                         # "8" by the parser.
        last_totalistic_context = "none" # Lets the parser remember the previous 
                                         # integer it encountered.
        notation_letter = "none"         # "none","a", "e", "i", etc.
        positive_or_inverse = "positive"
        inverse_list = []
        
        for x in rulestring:
            if x == "S" or x == "B" or x.isdigit() or x == "\n":
                last_totalistic_context = totalistic_context   
                totalistic_context = x                         
                if last_totalistic_context != "none"  and notation_letter == "none":
                    self.writetransition(bs, last_totalistic_context, "none",[])             
                if last_totalistic_context != "none" and  positive_or_inverse == "inverse":
                    self.writetransition(bs, last_totalistic_context, "none", inverse_list)
                 # Now lets get ready to move on to the next character.
                notation_letter = "none"
                inverse_list = []
                positive_or_inverse = "positive"
                if x == "S" or x == "B":
                    totalistic_context = "none"
                if x == "S":
                    bs = "1,"
                if x == "B":
                    bs = "0,"
            elif x == "-":
                positive_or_inverse = "inverse"
            elif x in ["c", "a", "e", "k", "i", "n", "j", "y", "q", "r", "w", "t", "z"] and totalistic_context != "none":
                if positive_or_inverse == "positive":
                   notation_letter = x
                   self.writetransition(bs, totalistic_context, notation_letter, [])   
                else:
                   notation_letter = x
                   inverse_list.append(x)
    
    #Recursive subroutine used in gridtostr(). Uses a 1-item list to simulate call-by-reference.
    def gridtostr_0(self, n, coords, size, str_):
        if n == 0:
            if tuple(coords) in self.grid:
                str_[0] += "O"
            else:
                str_[0] += "."
        else:
            for i in xrange(size[self.dims-n],size[2*self.dims-n]+1):
                tempcoords = coords[:]
                tempcoords.append(i)
                self.gridtostr_0(n-1, tempcoords, size, str_)
            str_[0] += "\n" * (1<<(n-1))
    
    #Find the dimensions of the grid
    def dimsOf(self, grd):
        if len(grd) == 0:
            return None
        rtn = list(grd.keys()[0])*2
        for i in grd:
            for j in xrange(len(i)):
               if i[j] > rtn[j+self.dims]:
                   rtn[j+self.dims] = i[j]
               elif i[j] < rtn[j]:
                   rtn[j] = i[j]
        return rtn
    
    #Converts the grid to a plaintext string
    def gridtostr(self):
        if self.empty():
            return ""
        size = self.dimsOf(self.grid)
        str = [""]
        self.gridtostr_0(self.dims, [], size, str)
        return str[0]
    def printgrid(self):
        print self.gridtostr()
    
    #For outer-totalistic rules, input the rulestring with transition numbers separated by commas.
    def setrule(self, rulestring):
        if self.hensel:
            return self.parseHensel(rulestring)
        rsplit = rulestring.lower().split("/")
        if len(rsplit[0]) and rsplit[0][0] == "b":
            self.b = map(int, rsplit[0][1:].split(","))
            self.s = map(int, rsplit[1][1:].split(","))
        else:
            self.b = map(int, rsplit[0][len(rsplit[0]) and rsplit[0][0] == "s":].split(","))
            self.s = map(int, rsplit[1][len(rsplit[1]) and rsplit[1][0] == "s":].split(","))
        self.rule = ([i in self.b for i in xrange(len(self.nbhd))], [i in self.s for i in xrange(len(self.nbhd))])
        self._firstrule = min(self.b[0] if len(self.b) else len(self.nbhd) + 1, self.s[0]+1 if len(self.s) else len(self.nbhd+1))
    
    def getrulestring(self):
        if self.hensel:
            return self.rulestring
        else:
            string = "B"
            string += ",".join(map(str, self.b))
            string += "/S"
            string += ",".join(map(str, self.s))
            return string
    
    #Parse a plaintext representation of the grid
    def parsegrid(self, string, dims):
        self.grid = {}
        string = string.replace(" ", "").replace("\n", "").replace("\r", "")
        cds = [0 for i in xrange(self.dims)]
        if len(string) == 0:
            return
        if string[0] == "O":
            self.grid[tuple([0 for i in xrange(self.dims)])] = 0
        while True:
            brk = False
            for i in list(xrange(self.dims))[::-1]:
                if cds[i] != dims[i]-1:
                    cds[i] += 1
                    break
                elif i:
                    cds[i] = 0
                else:
                    brk = True
                    break
            if brk:
                break
            q = 0
            for i in xrange(self.dims):
                qq = 1
                for j in xrange(i):
                    qq *= dims[j]
                q += qq*cds[i]
            if string[q].upper() == "O":
                self.grid[tuple(cds[::-1])] = 0
    
    #Returns a RLE representation of the whole grid (for 2D rules only)
    def makerle(self):
        if self.empty():
            return "x = 0, y = 0, rule = " + self.getrulestring()#.replace(",", "") + "\n!"
        gd = self.grid.keys()
        gd.sort()
        if self.dims != 2:
            return "Error: Invalid call of makerle() with dimensionality != 2."
        rctr = 0
        dims = self.dimsOf(self.grid)
        prev = (dims[0], dims[1]-1)
        dims2 = (dims[2]-dims[0]+1, dims[3]-dims[1]+1)
        rleh = "x = " + str(dims2[1]) + ", y = " + str(dims2[0]) + ", rule = " + self.getrulestring()#.replace(",", "")
        rleh += "\n"
        rle = ""
        for i in gd:
            if i[0] > prev[0]:
                rle += rlstr(rctr) + "o" + rlstr(i[0]-prev[0]) + "$" + ((rlstr(i[1]-dims[1])+"b") if (i[1]>dims[1]) else "")
                rctr = 1
            elif i[1]-1 == prev[1]:
                rctr += 1
            else:
                rle += (rlstr(rctr) + "o" if rctr else "") + rlstr(i[1]-prev[1]-1) + "b"
                rctr = 1
            prev = i
        rle += rlstr(rctr) + "o!"
        rle2 = ""
        while len(rle) > 67:
            rle2 += rle[:67] + "\n"
            rle = rle[67:]
        return rleh + rle2 + rle
    
    #Parse a RLE and write it to the grid
    def parserle(self, rle):
        header, q = "", []
        try:
            header, q = rle.split("\n")[0], rle.split("\n")[1:]
        except:
            header, q = rle.split("\r")[0], rle.split("\r")[1:]
        body = "".join(q)
        header = header.replace(" ", "")
        dims = []
        pos = 0
        for i in (2,3):
            pos += i
            str_ = ""
            while header[pos] in "0123456789":
                str_ += header[pos]
                pos += 1
            dims.append(str_)
        pos += 6
        if self.empty():
            rule = ""
            try:
                while True:
                    rule += header[pos]
                    pos += 1
            except:
                pass
            self.setrule(rule)
        body2 = ""
        i = 0
        while i < len(body):
            n = ""
            while body[i] in "0123456789":
                n += body[i]
                if body[i+1] not in "0123456789":
                    body2 += body[i+1] * (rlint(n)-1)
                    break
                i += 1
            else:
                body2 += body[i] * rlint(n)
            i += 1
        lines = body2.split("$")
        coords = [0,0]
        try:
            while True:
                try:
                    while True:
                        if lines[coords[0]][coords[1]] == "o":
                            self.grid[tuple(coords)] = 0
                        coords[1] += 1
                except:
                    coords[1] = 0
                    coords[0] += 1
                    lines[coords[0]][coords[1]] if len(lines[coords[0]]) else 0
        except:
            pass
    
    #Generate a random soup (50% density) with given dimensions
    def gensoup(self, *args):
        if len(args) == 1:
            args = args[0]
        #Emulate recursion:
        q = [[]]
        for i in xrange(self.dims):
            q = [j + [k] for j in q for k in xrange(args[i], args[i+self.dims])]
        soup = [tuple(i) for i in q]
        for i in soup:
            if round(random()):
                self.grid[i] = 0
    
    def reset(self):
        self.grid = {}
        self.gen, self.t1, self.t2, self.t3 = 0, 0, 0, 0
    
    #Run forward in time a given number of generations (optionally printing each one)
    def run(self, gens, print_=False, until = False):
        for i in xrange(gens):
            if (until and self.gen == gens) or self.empty():
                return
            self.step()
            if print_:
                self.printgrid()
                print self.gen
    
    def full_copy(self):
        ca = None
        if self.hensel:
            ca = CellularAutomaton(hensel=True)
        else:
            ca = CellularAutomaton(self.dims, lambda *args: tuple(args) in self.nbhd, self.range_, self.getrulestring())
        ca.grid = self.grid.copy()
        return ca
    
    #Return the grid translated
    def shift(self, *args):
        grd = {}
        for i in self.grid:
            grd[tuple(map(lambda x, y: x+y, self.grid[i], args))] = 0
        return grd
    
    #Rotate a/the grid and return it (for 2D rules only)
    def rotate2d(self, quadrant, x = 0, y = 0, origrd = None):
    	quadrant = (quadrant+4)%4
        if origrd is None:
            origrd = self.grid
        grd = {}
        for i in origrd:
            grd[(i[1] + int(y) + int(x), -i[0] + int(y) - int(x))] = 0
        if quadrant == 1:
            return grd
        else:
            return self.rotate2d(quadrant-1, x, y, grd)
    
    #Paste a pattern onto the grid
    def paste(self, grd, dims, mode = "OR", quadrant = None):
        if isinstance(grd, CellularAutomaton):
            grd = grd.grid
        lambdas = {"OR": lambda x: True,
                   "XOR": lambda x: not x,
                   "AND": lambda x: x}
        if quadrant is not None:
            ds = self.dimsOf(grd)
            grd = self.rotate2d(quadrant, (ds[2]+ds[0])/2, (ds[3]+ds[1])/2, grd)
        for i in grd:
            pos = tuple(map(lambda x, y: x+y, i, dims))
            q = pos in self.grid
            if lambdas[mode](q):
                self.grid[pos] = 0
            elif q:
                del self.grid[pos]

#For optimization purposes; times how long it takes to run the R-pentomino to stabilization.
def timeR(ca=None):
    if ca is None:
        pass#ca = CellularAutomaton(2, lambda *args: True, 1)
    #ca.setrule("B3/S2,3")
    ca = CellularAutomaton(hensel=True, rule="B3/S23")
    tot, t1, t2, t3 = 0, 0, 0, 0
    for i in xrange(10):
        ca.parsegrid("OO.\n.OO\n.O.", (3, 3))
        ca.run(1103)
        print ca.t1+ca.t2+ca.t3-tot, ca.t1-t1, ca.t2-t2, ca.t3-t3
        tot = ca.t1+ca.t2+ca.t3
        t1 = ca.t1
        t2 = ca.t2
        t3 = ca.t3
    print (ca.t1+ca.t2+ca.t3)/10, ca.t1/10, ca.t2/10, ca.t3/10
    ca.printgrid()
