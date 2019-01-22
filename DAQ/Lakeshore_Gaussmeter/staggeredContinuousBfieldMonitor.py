import src.LS_425    as LS
import config.config as cfg
import sys           as sy
import time          as tm
import                  os

if __name__ == "__main__":
    args = sy.argv[1:]
    if len(args) > 0:
        if len(args) == 1:
            fname = args[0]
        else:
            sy.exit('Invalid command-line arguments: %s' % (' '.join(args)))
    else:
        fname = None

    #Every time the Bfield is read, turn on and off the Gaussmeter
    while True:
        try:
            os.system('python ../../Control/Synaccess_Cyberswitch/commandSwitch.py ON 4')
            tm.sleep(10)
            for n in range(10): #Try to read field 10 times
                ls = LS.LS_425(cfg.SRSPort)
                b  = ls.get_bfield()
                del ls
                if b == 0: #Try connection again
                    continue
                else:
                    break
            os.system('python ../../Control/Synaccess_Cyberswitch/commandSwitch.py OFF 4')
            if fname:
                f = open(fname, 'a')
                f.write('%-15d %.02f\n' % (tm.time(), float(b)))
                f.close()
            print "[%d]  DC Field = %.02f G" % (tm.time(), float(b))
            tm.sleep(600) #Read once every ~10 minutes
        except KeyboardInterrupt:
            break
