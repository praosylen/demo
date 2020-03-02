# demo
Contains various example programs I've written. Most are obsolete at this point.

Contents:

casim.py

A general-purpose cellular automaton simulator in pure Python. Supports non-weighted outer-totalistic rules on hyperrectangular grids of all dimensionalities and all neighborhoods, as well as 2-dimensional Moore-neighborhood isotropic non-totalistic rules. See msrc.py for a demonstration.

Also includes casim.py.ipynb, a more in-depth explanation of casim's capabilities.


msrc.py

A search program for patterns that take a long time to stabilize ("methuselahs") in Conway's Game of Life (and related cellular automata). It's obsolete but serves to demonstrate some of casim.py's abilities.


trivalent-universe.py

A simulation of what I like to call a "trivalent" universe: one where Newton's Second Law is F=mj, and thus acceleration, not velocity, is constant in the absence of an external force. Contains a demonstration of an "orbit" in such a universe, best viewed on a terminal sized 100 x 51 or larger. Highly incomplete, and originally intended to be used in an ASCII terminal-window game, hence some of the commented-out blocks.


imnf.py

A parser for IMNF (Intermediate Musical Notation Format), a type of ASCII musical notation that I developed to be easily human-readable as well as computer-parsable. Complete specs for IMNF exist only in my head, however. Plays a round that I wrote a while ago as a default. It's fairly incomplete (I'm still working on it), and probably the worst-commented thing I have in here as well as the worst coding style.


osrc.cpp

A search program for oscillators and "short wide" spaceships in Conway's Game of Life (and related cellular automata). Uses a depth-first search as its overall architecture, and lookup tables to speed computation (resulting in a maximum width limitation of 9, or possibly 10).
