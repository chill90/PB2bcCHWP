import src.LS_425    as LS
import config.config as cg
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
    if cg.use_moxa:
        LS425 = LS.LS_425(tcp_ip=cg.moxa_ip, tcp_port=cg.moxa_port)
    else:
        LS425 = np.LS_425(rtu_port=cg.ttyUSBPort)
    LS425 = LS.LS_425()
    b  = LS425.get_bfield()
    if fname:
        f = open(fname, 'a+')
        f.write('%-15d %.02f\n' % (tm.time(), float(b)))
        f.close()
    print "DC Field = %.02f G" % (float(b))
