import src.LS_425    as LS
import config.config as cfg
import sys           as sy
import time          as tm

if __name__ == "__main__":
    args = sy.argv[1:]
    if len(args) > 0:
        if len(args) == 1:
            fname = args[0]
        else:
            sy.exit('Invalid command-line arguments: %s' % (' '.join(args)))
    else:
        fname = None
    ls = LS.LS_425(cfg.SRSPort)
    b  = ls.get_bfield()
    if fname:
        f = open(fname, 'a+')
        f.write('%-15d %.02f\n' % (tm.time(), float(b)))
        f.close()
    print "DC Field = %.02f G" % (float(b))
