# demo
Contains various example programs I've written.

Contents:

casim.py
A general-purpose cellular automaton simulator in pure Python. Supports non-weighted outer-totalistic rules on hyperrectangular grids of all dimensionalities and all neighborhoods, as well as 2-dimensional Moore-neighborhood isotropic non-totalistic rules. See msrc.py for a demonstration.

msrc.py
A search program for patterns that take a long time to stabilize ("methuselahs") in Conway's Game of Life (and related cellular automata). It's obsolete but serves to demonstrate some of casim.py's abilities.

osrc.cpp
A search program for oscillators and "short wide" spaceships in Conway's Game of Life (and related cellular automata). Uses a depth-first search as its overall architecture, and lookup tables to speed computation (resulting in a maximum width limitation of 9, or possibly 10).
