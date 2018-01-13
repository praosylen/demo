import casim
from random import random
#from time import sleep
#Running CGoL as an isotropic non-totalistic rule is slightly faster than as an outer-totalistic rule.
ca = casim.CellularAutomaton(hensel=True)
ca.setrule("B3/S23")
def orientations(n, x, y):
    os = []
    bits = [int(not not(n&(1<<i))) for i in xrange(x*y)]
    os.append(bits)
    os.append(bits[::-1])
    os.append([qq for q in [bits[x*i:x*i+x][::-1] for i in xrange(y)] for qq in q])
    os.append(os[2][::-1])
    if x == y:
        os.append([qq for q in [bits[i::x] for i in xrange(x)] for qq in q])
        os.append(os[4][::-1])
        os.append([qq for q in [os[4][x*i:x*i+x][::-1] for i in xrange(y)] for qq in q])
        os.append(os[6][::-1])
    rtn = [int(''.join(['01'[i] for i in l][::-1]), 2) for l in os]
    return rtn

def search():
    
    #Used for some auxiliary things to help filter out r-pentominoes before they slow down the search unnecessarily
    rstates = [6,7,9,8,9,12,11,18,11,11]
    rgen = 0
    rtracking = False
    
    #All results found cracking the top 24 list:
    rs = []
    
    #The 24 highest maximum lifespans found so far:
    maxls = [0]*24
    
    #Dimensions of patterns:
    x, y = 5, 5
    
    try:
        for q in xrange(2**(x*y)):
            if q and not q % 100:
                print "Longest-lived patterns:", maxls
            #I used to do this to give my computer a chance to cool off:
            #if q and not q % 3000:
                #sleep(10)#sleep(30)
            #'''
            
            #Generate a random x by y pattern with density 1/2:
            for i in xrange(x):
                for j in xrange(y):
                    if random() > 0.5:
                        ca.grid[(i,j)] = 0
            
            '''#Generate all x by y patterns in succession
            if q < (2**(x*y)):
                if q != min(orientations(q, x, y)):
                    continue
                for i in xrange(x):
                    for j in xrange(y):
                        if q&(1<<(i+x*j)):
                            ca.grid[(i,j)] = 0
            else:
                raise KeyboardInterrupt()
            #'''
            #ca.parsegrid(".O.OOO..O", (3,3))
            #ca.parsegrid(str([("O" if random() > 0.5 else ".") for _ in xrange(256)]), (16,16))
            
            #Save information for future reference:
            r = ca.makerle()
            l = len(ca.grid)
            
            #Number of gens since it was confirmed to still be active
            lensucc = 0
            
            #Minimum and maximum populations in previous 400 gens
            min400 = l
            max400 = l
            
            #Populations during previous 400 gens
            l400 = [l for i in xrange(400)]
            #Eliminate false positives
            l400[399] = None
            
            #Previous two gens for comparison
            prev = {}
            prev2 = {}
            
            #Run it for 100000 gens to see when it stabilizes
            for i in xrange(100000):
                #Determine whether it becomes an r-pentomino relative, and if so, skip all that "running it to completion" nonsense.
                if ca.getrulestring() == "B3/S23" and i < 20:
                    if len(ca.grid) == 6:
                        rgen = 0
                        rtracking = True
                if rtracking:
                    if len(ca.grid) != rstates[rgen]:
                        rtracking = False
                    if rgen == 9:
                        print q, 116, ca.gen + 1095
                        rtracking = False
                        break
                    rgen += 1
                
                #If the pattern's gone, it's stabilized.
                if ca.empty():
                    print q+1, 0, ca.gen
                    if i > maxls[0]: #If it's in the top 24 current longest-lasting patterns
                        maxls = sorted(maxls[1:] + [i]) #Add it to the list while removing the previous 24th place
                        print r
                        rs.append((i, r))
                    break
                
                #Get population and perform comparisons with previous 400 populations
                l = len(ca.grid)
                lensucc += 1
                #If it escapes the min/max populations from the last 400 gens, reset stabilization counter
                if l < min400:
                    min400 = l
                    lensucc = 0
                elif l > max400:
                    max400 = l
                    lensucc = 0
                #These two checks don't seem to do anything, but the program works just fine without them.
                if l400[0] == min400:
                    min400 = min(l400)
                if l400[0] == max400:
                    max400 = max(l400)
                l400 = l400[1:] + [l] #Update list for previous 400 populations
                '''if lensucc == 400 '''
                #Test for population stabilization, period 12.
                cond = max(l400[::12]) == min(l400[::12]) and max(l400[1::12]) == min(l400[1::12]) and max(l400[2::12]) == min(l400[2::12]) and max(l400[3::12]) == min(l400[3::12])
                cond = cond and max(l400[4::12]) == min(l400[4::12]) and max(l400[5::12])== min(l400[5::12]) and max(l400[6::12]) == min(l400[6::12]) and max(l400[7::12]) == min(l400[7::12])
                cond = cond and max(l400[8::12]) == min(l400[8::12]) and max(l400[9::12])== min(l400[9::12]) and max(l400[10::12]) == min(l400[10::12]) and max(l400[11::12]) == min(l400[11::12])
                #print l400
                #If population has stabilized or the grid state has repeated (period 2), we'll assume the pattern has stabilized.
                if cond or prev2 == ca.grid:
                    adj = i - 397 * cond#200 * (lensucc == 400)
                    print q+1, len(ca.grid), adj
                    if adj > maxls[0]: #If it's in the top 24 current longest-lasting patterns
                        maxls = sorted(maxls[1:] + [adj]) #Add it to the list while removing the previous 24th place
                        print r
                        rs.append((adj, r))
                    break
                prev2 = prev
                prev = ca.grid
                ca.step()
            else: #It'll be a switch engine or a high-period oscillator most likely.
                print q+1, len(ca.grid), 100000
                print r
                rs.append((i, r))
            ca.reset()
    except KeyboardInterrupt:
        pass
    #Print results
    rs.sort()
    for i in rs:
        print i[0]
        print i[1]
search()