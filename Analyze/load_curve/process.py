from datetime import datetime
import numpy as np
from scipy.optimize import curve_fit
import csv, os, sys

WRITE_DIR = 'process'
MIN_RSQUARED = 0.5

def temp_reader(path, ch):
    """return list of temperature data [time, ch1, ...]"""
    data = []
    with open(path, 'r') as f:
        header = f.readline()
        for l in f:
            data.append([float(x) for i, x in enumerate(l.split()) if i==0 or i in ch])
    return data

def power_reader(path):
    """return list of power data [(initial) time, (final) power]"""
    data = []
    with open(path, 'r') as f:
        d = []
        for i, l in enumerate(list(f)):
            if (i % 7 == 0):
                t_format = '%Y-%m-%d %H:%M:%S'
                t = datetime.strptime(l[1:20], t_format)
                d.append(t.timestamp())
            elif (i % 7 == 4):
                j = l.index('=')
                k = l.index('W')
                d.append(float(l[j + 1:k]))
            elif (i % 7 == 6):
                data.append(d)
                d = []
    return data

def temp_steps(temp, time):
    """return list of steps of temperature data, each step is a list of [time, ch1, ...] 
    such that steps[k] includes data during the k+1th power change""" 
    steps, stp = [], []
    i, j = 0, 0
    while i < len(temp) and j < len(time):
        if (temp[i][0] >= time[j]):
            steps.append(stp)
            stp = []
            j += 1
        stp.append(temp[i])
        i += 1
    steps.append(temp[i:])
    return steps[1:]

def s_function(t, A, B, C, tau, t_0):
    return A/(np.exp((-t)/tau + t_0) + B) + C  

def s_p0(prev_fit):
    A, B, C, tau, t_0 = 1, 1, 10, 1, 0
    if prev_fit is not None:
        A = prev_fit[0]
        B = prev_fit[1]
        C = prev_fit[0]/prev_fit[1] + prev_fit[2]
    return np.array([A, B, C, tau, t_0])

def exp_function(t, A, B, C, tau, t_0):
    return A*(1 - B*np.exp(-t/tau + t_0)) + C  

def exp_p0(prev_fit):
    A, B, C, tau, t_0 = 1, 1, 10, 10, 0
    if prev_fit is not None:
        A = prev_fit[0]
        B = prev_fit[1]
        C = prev_fit[0] + prev_fit[2] 
        tau = max(prev_fit[3], tau)
    return np.array([A, B, C, tau, t_0])

def exp_final(fit):
    return fit[0] + fit[2] if fit else None

def curve_fitter(temp, curve_f, p0_f):
    """Fit stepped temperature data according to curve_f with initial parameters set by p0_f
    return a list of each steps' best fit parameters [[ch1 fit params], ...]
    and a list of each steps' r_squared [ch1 error, ...] """
    fits, errors = [], []
    for i, step in enumerate(temp):
        step = np.array(step)
        time_data = step[:,0] - step[0][0] 
        step_fit, step_error = [], []
        for ch in range(1, len(step[0])):
            temp_data = step[:,ch]
            p_0 = p0_f(fits[-1][ch - 1] if fits else None) 
            try:
                popt, pcov = curve_fit(curve_f, time_data, temp_data, p_0, bounds=(0, np.inf))
                residuals = temp_data- curve_f(time_data, *popt)
                ss_res = np.sum(residuals**2)
                ss_tot = np.sum((temp_data-np.mean(temp_data))**2)
                r_squared = 1 - (ss_res / ss_tot)
                if r_squared < MIN_RSQUARED:
                    raise RuntimeError("R-squared of %f below thereshold" % r_squared)
                step_fit.append(popt.tolist())
                step_error.append(r_squared)
            except RuntimeError as e:
                print("Step %d Channel %d Ignored: %s" % (i, TEMP_CHANNELS[ch-1], e))
                step_fit.append(None)
                step_error.append(None)
                continue
        fits.append(step_fit)
        errors.append(step_error)
    return fits, errors 

def final_temp(fits, func):
    """return list of each step's final temperatures, [ch1, ...], based on fitting"""
    return [[func(ch) for ch in stp] for stp in fits]

def result_writer(path, final_temp, fits, errors, power):
    with open(path, mode='w') as f:
        writer = csv.writer(f)
        writer.writerow(["Temp File", "Channels", "Power File"])
        writer.writerow([TEMP, TEMP_CHANNELS, POWER])
        writer.writerow(["Time", "Power", "Final temp", "Fits", "R-squared"])
        for p, t, f, e in zip(power, final_temp, fits, errors):
            writer.writerow([p[0], p[1], t, f, e])

def power_temp_writer(path, final_temp, power):
    with open(path, mode='w') as f:
        writer = csv.writer(f, delimiter='\t')
        header = ["Power(W)"]
        sigfig = lambda c: "%.2f" % c if c else None
        for ch in range(len(final_temp[0])):
            header.append("Ch %d(K)" % (TEMP_CHANNELS[ch]))
        writer.writerow(header)
        for p, t in zip(power, final_temp):
            writer.writerow(["%.2f" % p[1], *map(sigfig, t)])

def conductivity_calc(final_temp_single, power):
    """Calculate conductivity based on k = dP/dT. 
    Return list of [temp, k], where temp is the midpoint of the interval
    Requires final_temp_single to be a non-nested list (i.e. single channel)"""
    tp = final_temp_single
    conduct = []
    for i in range(len(power) - 1):
        k = (power[i+1][1] - power[i][1])/(tp[i+1] - tp[i])
        conduct.append([(tp[i+1] + tp[i])/2, k])
    return conduct

def conductivity_writer(path, conductivity, text = None):
    with open(path, mode='a') as f:
        writer = csv.writer(f, delimiter='\t')
        if text:
            writer.writerow([text])
        writer.writerow(["Temperature(K)", "Conductivity(W/K)"])
        sigfig = lambda c: ["%.2f" % c[0], "%.3f" % c[1]]
        writer.writerows(map(sigfig, conductivity))

def conductivity_process(final_temp, power, path):
    final_temp = np.array(final_temp)
    conductivities = []
    try:
        os.remove(path)
    except OSError:
        pass
    for ch in range(len(final_temp[0])):
        conductivity = conductivity_calc(final_temp[:,ch], power)
        conductivities.append(conductivity)
        text = "Ch " + str(ch + 1)
        conductivity_writer(path, conductivity, text)
    return conductivities

def read_arg():
    global DATA_DIR, WRITE_DIR, TEMP, POWER, TEMP_CHANNELS, RESULT, POWERTEMP, CONDUCT
    if len(sys.argv) < 3:
        DATA_DIR = 'data'
        WRITE_DIR = 'data/process'
        TEMP = 'srsTemperature_1539648659.txt'
        POWER = '20181015_CopperRodCondTest.txt'
        TEMP_CHANNELS = [1, 2]
        RESULT = 'result_srsTemperature_1539648659_20181015_CopperRodCondTest.csv'
        POWERTEMP = 'power_temp_srsTemperature_1539648659_20181015_CopperRodCondTest.txt'
        #CONDUCT = 'conductivity.txt'
        raise ValueError("No file given, default values used \nSpecify with 'python3 process.py temperature_file power_file'")

    temp_file = sys.argv[1]
    power_file = sys.argv[2]
    DATA_DIR = os.path.dirname(temp_file) 
    if os.path.dirname(power_file) != DATA_DIR:
        raise RuntimeError("Input files not in the same directory")
    WRITE_DIR = DATA_DIR+'/'+WRITE_DIR
    TEMP = os.path.basename(temp_file)
    POWER = os.path.basename(power_file)

    TEMP_CHANNELS = sorted(list(map(int, input('Temperature channel(s) to process (separated by space):').split())))
    suffix = TEMP[:-4] + "_" + POWER[:-4] 
    RESULT = "result_"+suffix+".csv"
    POWERTEMP = "power_temp_"+suffix+".txt"

def main():
    try:
        read_arg()
    except ValueError as e:
        print(e)
    except RuntimeError as e:
        print(e)
        sys.exit()
    temp = temp_reader(DATA_DIR+'/'+TEMP, TEMP_CHANNELS)
    power = power_reader(DATA_DIR+'/'+POWER)
    power_np = np.array(power)
    steps = temp_steps(temp, power_np[:, 0])
    f, e = curve_fitter(steps, exp_function, exp_p0)
    final_t = final_temp(f, exp_final)
    os.makedirs(WRITE_DIR, exist_ok=True)
    result_writer(WRITE_DIR+'/'+RESULT, final_t, f, e, power)
    power_temp_writer(WRITE_DIR+'/'+POWERTEMP,final_t, power)
    #conductivity_process(final_t, power, CONDUCT) work in progress

if __name__ == "__main__":
    main()
