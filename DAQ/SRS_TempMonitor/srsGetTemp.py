import src.SIM_900 as SIM
import config.config as cfg

if __name__ == "__main__":
    sim = SIM.SIM_900(cfg.SRSPort, cfg.SRSSlot)
    t = sim.get_temps()
    for i in range(len(t)):
        print "Ch %d = %.02f K" % (i, float(t[i]))
