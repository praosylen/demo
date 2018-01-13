import pyaudio
import numpy as np
import re
from random import random, randint

p = pyaudio.PyAudio()

fs = 44100
nps = 6


ndur = 1.0/nps

#Approximations to instrument Fourier series (for a given value of Fourier series).
#Currently only sine wave, clarinet, and something that sounds somewhat like an organ supported.
instruments = {
    0:[(1,1)],
    1:[(0.25,0.07),(0.42,0.06),(1,1),(2,0.04),(3,0.99),(4,0.12),(5,0.53),(6,0.11),(7,0.26),(8,0.5),(9,0.24),(10,0.07)],
	2:[(1,1),(2,0.09),(3,0.03),(4,0.12),(5,0.02),(6,0.07),(8,0.05)]
}
samples = []

#Multiply numpy arrays and truncate to dimension of smallest one.
def nicemult(a1, a2):
    if len(a1) < len(a2):
        a2 = a2[:len(a1)]
    elif len(a2) < len(a1):
        a1 = a1[:len(a2)]
    return a1*a2

#Generate a numpy array from a list of volume fixed points.
def volarray(pts):
    arr = np.empty([0]).astype(np.float32)
    for i in xrange(len(pts)-1):
        #Not the best solution to the zero-volume conundrum but I don't know what else to do:
        if not (pts[i][1] and pts[i+1][1]):
            arr = np.concatenate([arr, np.linspace(pts[i][1], pts[i+1][1], int((pts[i+1][0]-pts[i][0])*fs), False).astype(np.float32)])
        else:
            arr = np.concatenate([arr, np.geomspace(pts[i][1], pts[i+1][1], int((pts[i+1][0]-pts[i][0])*fs), False).astype(np.float32)])
    return arr

#Create an attack-decay-sustain-release volume profile from an articulation profile:
def profile(l, attv, attt, dect, sust, relt):
    rtn = None
    sust *= l
    sust -= relt
    if attt+dect > sust:
        r = sust/(attt+dect)
        decr = (attv-1)/dect
        rtn = [(0,0),(attt*r,attv*r),(sust,attv*r-(sust-attt*r)*decr),(sust+relt,0),(l,0)]
    else:
        rtn = [(0,0),(attt,attv),(attt+dect,1),(sust,1),(sust+relt,0),(l,0)]
    if attt == 0:
        rtn = [(0,attv)] + rtn[1:]
    if relt == 0:
        rtn = rtn[:2] + [(l,1)]
    if sust+relt >= l:
        rtn = rtn[:-2] + ([rtn[-1]] if rtn[-1] == (l,1) else [(l,0)])
    return rtn

'''print profile(2, 2, 0.25, 0.25, 0.25, 0.25)
()()'''

'''#print np.version.version
print volarray([[0,1],[1,2],[2,1]])
()()'''

#Create a numpy array containing data for a single note, based on pitch, instrument type, note duration, and a volume profile
def note(inst, volume, fs, duration, f):
    q = (reduce(lambda x, y: x+y, [np.sin(2*np.pi*np.arange(fs*duration)*f/fs*i)*j for i,j in instruments[inst]]))
    if isinstance(volume, int):
        return (q*volume).astype(np.float32)
    return nicemult(q, volume).astype(np.float32)

#Random useless wrapper for the note function that I was planning on using for other things but didn't
class Note:
    def __init__(self, t=None, inst=None, volume=None, fs=None, duration=None, f=None, data=None):
        if data is None:
            self.data = note(inst, volume, fs, duration, f)
        else:
            self.data = data
        self.t = t
        self.duration = duration
    def __add__(self, other):
        return Note(t=self.t, duration=self.duration, data=self.data+other.data)

#Parser for a pair of lines containing rhythm information
class Timing:
    def __init__(self, text):
        self.meta, self.text = text.split("\n")
        self.parse()
    def parse(self):
        i = 0
        time = 0
        prev = "-"
        self.times = []
        self.end = None
        loc_nps = nps
        loc_ndur = ndur
        while i < len(self.text):
            if self.text[i] in "|ij-" and prev in "|ij-":
                time += loc_ndur
                if prev == "|" and self.text[i] == "|":
                    time += loc_ndur*3
                self.times.append(time)
                prev = self.text[i]
            elif self.text[i] == " ":
                self.times.append(None)
            elif (self.text[i] in "eax." and prev in "|ij-eax.") or (self.text[i] in "|ij-" and prev in "eax."):
                time += loc_ndur/2
                self.times.append(time)
                prev = self.text[i]
            elif self.text[i] == "+" or prev == "+":
                time += loc_ndur/4
                self.times.append(time)
                prev = self.text[i]
            #print i, len(self.times), len(self.text)
            if i < len(self.meta) and self.meta[i] in "ij":
                j = i+1
                while j < len(self.meta) and self.meta[j] in "0123456789.":
                    j += 1
                loc_nps = float(self.meta[i+1:j])/60*(2 if self.meta[i] == "i" else 4)
                loc_ndur = 1.0/loc_nps
            i += 1
            if len(self.times) == 1:
                time = 0
                self.times[0] = 0
        while i > 0:
            i -= 1
            #print i, len(self.times), len(self.text)
            if self.times[i] is None:
                self.times[i] = self.times[i+1] if i+1 < len(self.times) else None
            elif self.end is None:
                self.end = self.times[i] + loc_ndur/2
'''t = Timing("\
i60\n\
|-i-i-i-a+|| -i-i-i-|")
print t.meta, t.text, t.times'''
artics = {"" :[1.5,0.01,0.02,1,0.03],
          "|":[1.5,0.01,0.02,0.80,0.03],
          "*":[1.5,0.01,0.02,0.25,0.01],
          "?":[3,0.01,0.04,1,0.03],
          ">":[3,0.01,0.04,0.80,0.03],
          "v":[3,0.01,0.04,0.25,0.01],
          "+":[1.25,0.02,0.03,1,0.03],
          "(":[1,0,0.00000000000001,1,0],
          ")":[1,0,0.00000000000001,1,0],
}

aux_i = 1 #Used later in aux(); initialized here to facilitate error message printing
#Parser for a pair of lines representing a musical line plus dynamics information
class Line:
    c_dyns = "nopPFfg"
    contrast = 2
    def __init__(self, notes=None, text=None, timing=None):
        self.notes = notes
        self.text = text
        if len(self.text) == 2 and len(self.text[0]) > 1: #Fails on a 1-note-long piece, but oh well.
            self.text, self.dyns = self.text
            if self.dyns[0] == " ":
                self.dyns = "F" + self.dyns[1:]
        else:
            self.dyns = "F" #mf
        self.text = self.text.replace("c#","C ").replace("d#","D ").replace("e#","f ").replace("f#","F ").replace("g#","G ").replace("a#","A ").replace("b#","c ").replace(
                                 "c.","b ").replace("d.","C ").replace("e.","D ").replace("f.","e ").replace("g.","F ").replace("a.","G ").replace("b.","A ")
        self.dyns = self.dyns.replace("ppp", "n  ").replace("pp", "o ").replace("mp", "P").replace("mf", "F").replace("ff", "g ")
        self.timing = timing
        if self.notes is None:
            self.parsedyns()
            #print self.da
            self.notes = self.parse(self.text)
    def compile(self, play=False):
        curr = 0
        arr = []
        for i in self.notes:
            arr.append(note(1, 0, fs, i.t-curr, 440.0))
            arr.append(i.data)
            #print len(arr[-1])
            curr = i.t+i.duration
        if play:
            samples.append(np.concatenate(arr*4))#Mystified as to why the *4 is necessary
            return
        return np.concatenate(arr*4)
    def parsedyns(self):
        self.da = []
        rchng = 0
        currdyn = "F"
        for i in xrange(len(self.text)+1):
            if i < len(self.dyns) and self.dyns[i] in self.c_dyns:
                currdyn = self.dyns[i]
                rchng = 0
                self.da.append(0.005*self.contrast**(self.c_dyns.index(self.dyns[i])-3))
            elif i < len(self.dyns) and self.dyns[i] in "cd":
                self.da.append(self.da[-1])
                j = i
                while j < len(self.dyns) and self.dyns[j] not in self.c_dyns:
                    j += 1
                rchng = (self.c_dyns.index(self.dyns[j])-self.c_dyns.index(currdyn))/(self.timing.times[j]-self.timing.times[i])
            elif rchng and 0 < i < len(self.timing.times) and self.timing.times[i] != " ":
                self.da.append(self.da[-1]*self.contrast**(rchng*((self.timing.times[i]-self.timing.times[i-1]) if 0 < i < len(self.timing.times) else 0)))
            else: self.da.append(self.da[-1])
    def parse(self, text):
        notes = []
        octave = 0
        note = re.compile("[a-gA-G][|\*?v>+()]?[\^\_]*-*")
        qq = re.finditer(note, text)
        qqq = [i.start() for i in qq]
        q = []
        for i in qqq:
            j = i+1
            a = ""
            while j < len(text) and text[j] not in "cCdDefFgGaAb!":
                if text[j] in "|*?v>+()":
                    a = text[j]
                if text[j] == " " and j < len(text)-1 and self.timing.times[j] != self.timing.times[j+1]:
                    break
                j += 1
            q.append((i,j,a))
        #print text
        for ind, z, a in q:
            #print "Parsing..."
            try:
                i = text[ind:z]
                octave += i.count("^") - i.count("_")
                #l = ndur*(1+i.count("-"))
                l = (self.timing.times[z] if z < len(self.timing.times) else self.timing.end) - self.timing.times[ind]
                #ind = text.index(i)
                prev = text[:ind]
                #t = ndur*(ind-prev.count("^")-prev.count("_"))
                t = self.timing.times[ind]
                artic = artics[a]
                notes.append(Note(t, 1, nicemult(volarray(zip(self.timing.times[ind:z+1], self.da[ind:z+1])),volarray(profile(l,*artic))), fs, l, self.freq(i[0], octave)))
            except:
                print "Error at note/articulation line %i, position %i!" % (aux_i+1, ind)
                raise
            #print t, self.timing.end
        notes.append(Note(self.timing.end, 0, 0, fs, 1.0/fs, 1))
        #print q
        #return [Note(i*0.125, 1, 0.05, fs, 0.125, self.freq(text[i],0)) for i in xrange(len(text))]
        return notes
    def freq(self, name, oct):
        return 440.0 * 2**("cCdDefFgGaAb".index(name)/12.0 + oct - 0.75)
#Line(text="cdef-ef-gagg_-------", timing=t).compile(True)

def aux(x): #A hack to print stuff in the middle of a list comprehension.
    global aux_i
    print aux_i, "lines processed."
    aux_i += 1
    return x

#Main parser
class Parsed:
    def __init__(self, text):
        self.text = text
        self.lines = text.split("\n")
        #print self.lines
        self.timing = Timing("\n".join(self.lines[:2]))
        self.lines = self.lines[2:]
        self.lines = [self.lines[i:i+2] for i in xrange(0,len(self.lines),2)]
        self.lines = [aux(Line(text=i, timing=self.timing).compile()) for i in self.lines]
        self.end = min(len(i) for i in self.lines)
        self.lines = [i[:self.end] for i in self.lines]
    #Taken largely from a PyAudio example program that I forget where I found.
    def play(self):
        samples = [reduce(lambda a,b: a+b, self.lines)]
        stream = p.open(format=pyaudio.paFloat32,
                        channels=1,
                        rate=fs,
                        output=True)
        
        for i in samples:
            stream.write(i)
        stream.stop_stream()
        stream.close() 
        #print min(samples[0])
        p.terminate()
'''
with open("seasons/fw.imnf", "r") as f:
    Parsed("\n".join([i[0:-1] for i in f.readlines()[1:]]).replace("\n\n","\n")).play()
'''
Parsed("""i170
|-i-i-|-i-i-|-i-i-|-i-i-|-i -i -|-i-i-| -i-i -|-i-i -|-i-i-| -i-i-|-i-i-| -i-i-|-i  -i-|-i-i-|-i-i-|- i-i-| -i-i-|-i-i-|-i-i-|-i-i-|-i-i-|-i-i-|-i-i-|-i-i-|-i -i -|-i-i-| -i-i -|-i-i -|-i-i-| -i-i-|-i-i-| -i-i-|-i  -i-|-i-i-|-i-i-|- i-i-| -i-i-|-i-i-|-i-i-|-i-i-|-i-i-|-i-i-|-i-i-|-i-i-|-i-i-|-i-i-|-i-i-|-i-i-|-i -i -|-i -i -| -i -i -| -i-i -| -i-i -| -i-i -| -i-i-| -i-i-| -i  -i-| -i  -i-|-i  -i-|- i-i-| - i-i-| - i-i-| -i-i-|-i-i-|-i-i-|-i-i-|-i-i-|-i-i-|-i -i -|-i -i -| -i -i -| -i-i -| -i-i -| -i-i -| -i-i-| -i-i-| -i  -i-| -i  -i-|-i  -i-|- i-i-| - i-i-| - i-i-| -i-i-|-i-i-|-i-i-|-i-i-|-i-i-|-i-i-|-
c-----d-----e-----g-----b-c^-b_-d-e-f-f#-g-a.-b---c^-d-----g_-a-g-e---b-c^--d--c-a._-g-fef--dg-----ac^----f_ge---d-c-gag-------cedcc-----d-----e-----g-----b-c^-b_-d-e-f-f#-g-a.-b---c^-d-----g_-a-g-e---b-c^--d--c-a._-g-fef--dg-----ac^----f_ge---d-c-gag-------cedcc-----c------------     c-----d-----e-----g-----b-c^-b_-d-e -f -f#-g -a.-b ---c^-d ---- -g_-a-g -e ---b-c^--d--c -a._-g-f ef  --dg--  ---ac^----f_g e---d - c-gag -------cedcc-----d-----e-----g-----b-c^-b_-d-e -f -f#-g -a.-b ---c^-d ---- -g_-a-g -e ---b-c^--d--c -a._-g-f ef  --dg--  ---ac^----f_g e---d - c-gag -------cedcc-----c------------------ 
 
                                                                                                                                                                                                                                                                                                    c-----d-----e-----g-- -- -b-c^-b_-d -e -f -f#-g-a.-b ---c^-d ---- -g_-a-g-e ---b-c^--  d--c -a._-g-fef  --dg- ----a c^----f_g e---d -c-gag-------cedcc-----d-----e-----g-- -- -b-c^-b_-d -e -f -f#-g-a.-b ---c^-d ---- -g_-a-g-e ---b-c^--  d--c -a._-g-fef  --dg- ----a c^----f_g e---d -c-gag-------cedcc-----c------------
 
                                                                                                                                                                                                                                                                                                          c-----d-----e-- -- -g-- -- -b -c^-b_-d -e-f -f#-g-a.-b ---c^-d -----g_-a-g-e --  -b-c^--  d--c-a._-g-fe f--dg - ----a c^----f_ge---d-c-gag-------cedcc-----d-----e-- -- -g-- -- -b -c^-b_-d -e-f -f#-g-a.-b ---c^-d -----g_-a-g-e --  -b-c^--  d--c-a._-g-fe f--dg - ----a c^----f_ge---d-c-gag-------cedcc-----c------
 """).play()
 
#The following don't actually work any more, due to features that I've added for other reasons:

"""#Uncomment for "In the Hall of the Mountain King" arranged for fake clarinet choir:
#
'''
Line(text="cdDfgDg-FdF-fCf-cdDfgDgc^A_gDgA--Gg g").compile(True)
Line(text="c_ D c D d F C f c D c d A_ D^ b_ D^ c c").compile(True)
Line(text="D_ g D g F a f G D g D A D A d b D D").compile(True)
Line(text="g_ c^ g_ b A d^ G_ b c^ c g_ c^ g_ D^ f_ g g D").compile(True)
samples = [reduce(lambda a,b:a[:955544]+b[:955544],samples)]
#'''
#Uncomment for a round that's too hard for mere mortals to sing, but not for computers:
#
'''
text = "c_-----d-----e-----g-----b-c^-b_-d-e-f-F-g-G-b---c^-d-----g_-a-g-e---b-c^--d--c-G_-g-fef--dg-----ac^----f_ge---d-c-gag-------cedcc"
text += text[2:] + "-----c-----            c"
Line(text=text).compile(True)
text = "c_-----c^"+text[2:]
Line(text=text).compile(True)
text = "c_-----c-----c_"+text[9:]
Line(text=text).compile(True)
for i in samples:
    print len(i)
#()()
samples = [reduce(lambda a,b:a[:7791064]+b[:7791064],samples)]
#'''
#Uncomment for random chord progression generator
#
'''
l = 6
cycle = "cCdDefFgGaAb"
def randchord():
    def freq(name, oct):
        return 440.0 * 2**(cycle.index(name)/12.0 + oct)
    n = 3
    r = random()
    if r > 0.9:
        n = 5
    elif r > 0.6:
        n = 4
    """
    """intervals = {1:1
                 2:3
                 3:7
                 4:11
                 5:15
                 6:16
                 7:19
                 8:21
                 9:23
                 10:24
                 11:25}"""
    """
    intervals = [[1,2,2,3,3,3,3,4,4,4,4,5,5,5,5,6,7,7,7,8,8,9,9,10,11],
                 [1,1,1,2,2,2,2,2,3,3,3,3,3,4,4,4,4,4,5,5,5,5,6,7,7,8,9,10,11],
                 [1,1,1,1,1,1,2,2,2,2,2,2,2,2,2,2,3,3,3,3,3,3,3,3,4,4,4,4,4,4,4,5,5,5,5,5,5,6,7,7,7,8,8,9,9,10,11]]
    chord = [randint(0,11)]
    for i in xrange(n-1):
        chord.append(chord[-1]+intervals[n-3][randint(0,len(intervals[n-3])-1)])
    c2, ct = 0,0
    for i in chord:
        c2 += (i+1 in chord) + (i+13 in chord)
        ct += (i+6 in chord) + (i+18 in chord)
        if (i-11 in chord or i+1 in chord or i+13 in chord) and (i-8 in chord or i+4 in chord or i+16 in chord):
            randchord()
            return
        if (i-9 in chord or i+3 in chord or i+15 in chord) and (i-8 in chord or i+4 in chord or i+16 in chord):
            randchord()
            return
    if c2 > 1 or ct > 1:
        randchord()
        return
    samples.append(reduce(lambda a,b: a+b,map(lambda n:note(1,0.05,fs,ndur*24,freq(cycle[n%12],n/12-(n%12)/12-2)),chord)))
    print "".join(map(lambda n:cycle[n%12]+"^"*(n/12-(n%12)/12),chord))
for i in xrange(l):randchord()
"""
"""Results:
W5:
FDA
CFa
FAC
FDbF^
CGA
gcG

W6:
fAa.
abCDe
cfa
dfAD
gAbD
aebc^

W7:
Cfb
egb
Gfad^
dCfa
CeGb
cDgd

W3:
cgA
fAcf
acf
bda
gcec^
dAeg

W5:
dae^
AD^g^
ebD^
dbf^
bD^F^
cDfab

W8:
Ac^d^g^
Ac^a^f^^F^^
AG^C^^a^^
dDaC^
AF^b^
Ac^C^

W4:
CaF^
CfA
egc^
bF^C^^
bF^G^b^
cdeac^

W4:
gd^a^
gAd^
bd^F^d^^
dAg^
Cfab
fAd^

W7:
eD^a^
fGD^f^
bd^f^a^
CdF
bd^C^^
daF^b^

W6:
GbC^f^
aF^A^
cfg
DAf^
Ag^a^d^^g^^
fFD^e^

W5:
aC^e^
Dgb
DC^e^
cfA
dfA
eac^

W5:
fabd^
bF^G^
AD^f^
deG
eC^G^
gGC^

W5:
cFad^
fGC^
ag^C^^
GC^F^
cCdec^x
eFb

W6:
Ae^f^a^
dDFA
fae^g^
Ac^d^
fFa
ad^a^A^f^^

W7:
be^G^
AG^b^
fe^b^
CfA
Fd^f^x
AbD^g^x

W3:
CeD^
cfG
ebe^G^
CGC^
fD^G^C^^
Ge^b^

W5:
abG^F^^
Dc^g^
FAC^
ceG
be^G^
gD^b^

W5:
cfg
FbC^d^
fD^e^x
debc^d^
gd^g^
ac^f^

W3:
be^b^
bF^a^
aC^F^a^
dC^G^
DAg^
ceF

W6:
cbc^f^x
Gf^D^^?
FbF^
ebD^
aC^F^
Ad^e^

W6:
gf^b^
CDC^
eac^
dFAc^
fabC^?
gc^g^f^^G^^X

W6:
cad^
ge^D^^
eC^G^
ceGc^
DGc^C^
egaC^

W4:
egAc^
Gc^D^
Ceb
DgA
DeaC^x

W5:
AG^e^^
CeF
egd^
fGb
bC^f^
cDA

W5:
bc^d^F^
FGd^
DFG
cgA
GAc^d^?
DgD^?

W4:
GAc^
dDA
Gd^e^
af^A^
DAc^
eac^

W4:
AbC^
ebC^
DGb
Ad^A^
eaf^
Ac^e^a^

W3:
eac^d^e^
cgc^
DeD^G^
dbd^
CFA
faA"""#'''

'''So that this is legal, here's a copy of the PyAudio license (hopefully covering the PyAudio example program that I use as the core audio component of this program):

PyAudio is distributed under the MIT License:
Copyright (c) 2006 Hubert Pham

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''