import TC_340 as TC

if __name__ == "__main__":
    tc = TC.TC_340()
    t = tc.get_temps()
    print "CH A = %.02f K" % (t[0])
    print "CH B = %.02f K" % (t[1])
    print "CH C = %.02f K" % (t[2])
    print "CH D = %.02f K" % (t[3])
