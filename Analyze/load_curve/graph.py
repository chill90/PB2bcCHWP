from process import exp_function, temp_reader, temp_steps
import matplotlib.pyplot as plt
import numpy as np
import csv, sys, os 

DATA_DIR = '..'
GRAPH_DIR = '../graph'
DISPLAY = True
SAVE = True

def csv_reader(path, delimit = ','):
    with open(FILE_DIR+'/'+path, "r") as f:
        reader = csv.reader(f, delimiter = delimit)
        return list(reader)

def plot_curve(save = False):
    def plot(start_t, end_t, sample, fit, curve_func):
        t_data = np.linspace(start_t, end_t, sample)
        fit_t = np.linspace(0, end_t - start_t, sample)
        temp_data = curve_func(fit_t, *fit)
        plt.plot(t_data, temp_data, color = 'b')
        return t_data, temp_data
    result = csv_reader(RESULT)
    temp_file = DATA_DIR+'/'+result[1][0]
    channels = eval(result[1][1])
    result = result[3:]
    for r in result:
        for i in range(len(r)):
            r[i] = eval(r[i])
    try:
        data = np.array(temp_reader(FILE_DIR+'/'+temp_file, channels))
        steps = temp_steps(data, [r[0] for r in result])
        plot_data = True
    except IOError:
        plot_data = False
        print("Original temperature data not found. It's not plotted.")
    for ch in range(len(result[0][2])):
        i = 1
        plt.figure(ch)
        for t, p, temp, fit, r2 in result:
            if temp[ch] is None:
                continue
            t_end = t + fit[ch][3] * 10
            if i < len(result):
                t_end = max(t_end, result[i][0]) 
            n = (t_end - t) / 10
            t, temp = plot(t, t_end, n, fit[ch], exp_function)
            i+=1
        if plot_data:
            plt.plot(data[:, 0], data[:, ch+1], '.', color='r', label = "data")
        plt.title('Ch ' + str(channels[ch]))
        plt.xlabel('Time (s)')
        plt.ylabel('Temperature (K)')
        plt.legend(loc = 'upper left')
        if save:
            plt.savefig('%s/%s/%s_channel_%s.png' % (FILE_DIR, GRAPH_DIR, RESULT[:-4], ch))

def plot_power_temp(save = False):
    p_t = csv_reader(POWERTEMP, '\t')
    channels = [ch[3] for ch in p_t[0][1:]]
    p_t = p_t[1:]
    for ch in range(len(p_t[0]) - 1):
        plt.figure(2 + ch)
        p_t_channel = np.array([(x[ch+1], x[0]) for x in p_t if x[ch+1]!=""]).astype(float)
        plt.scatter(p_t_channel[:, 0], p_t_channel[:, 1])
        plt.title('Ch ' + channels[ch])
        plt.ylabel('Power (W)')
        plt.xlabel('Temperature (K)')
        if save:
            plt.savefig('%s/%s/%s_channel_%s.png' % (FILE_DIR, GRAPH_DIR, POWERTEMP[:-4], ch))

def plot_conductivity():
    def plot():
            plt.figure(4 + ch)
            plt.scatter(temp, cond)
            plt.title('Ch ' + str(ch+1))
            plt.ylabel('Conductivity (W/K)')
            plt.xlabel('Temperature (K)')

    conduct = csv_reader(CONDUCT, '\t')[2:]
    ch = 0
    temp, cond = [], []
    i = 0
    while i < len(conduct):
        if len(conduct[i]) == 1:
            plot()
            temp, cond = [], []
            i += 2
            ch += 1
        else:
            temp.append(float(conduct[i][0]))
            cond.append(float(conduct[i][1]))
            i += 1
    plot()

def read_arg():
    global RESULT, POWERTEMP, CONDUCT, FILE_DIR
    if len(sys.argv) < 3:
        RESULT = 'result_srsTemperature_1539648659_20181015_CopperRodCondTest.csv'
        POWERTEMP = 'power_temp_srsTemperature_1539648659_20181015_CopperRodCondTest.txt'
        FILE_DIR = 'data/process' 
        raise ValueError("No file given, default values used \nSpecify with 'python3 graph.py result_file power_temp_file'")
    result_file = sys.argv[1]
    p_t_file = sys.argv[2]
    RESULT = os.path.basename(result_file)
    POWERTEMP = os.path.basename(p_t_file) 
    FILE_DIR = os.path.dirname(result_file)

def main():
    try:
        read_arg()
    except ValueError as e:
        print(e)
    os.makedirs(FILE_DIR+'/'+GRAPH_DIR, exist_ok=True)
    plot_curve(SAVE)
    plot_power_temp(SAVE)
    #plot_conductivity()
    if DISPLAY:
        plt.show()

if __name__ == "__main__":
    main()
