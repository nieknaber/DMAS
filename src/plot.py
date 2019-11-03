import numpy as np 
import matplotlib.pyplot as plt
import pandas as pd

limit0 = 100000
limit1 = 100000
limit2 = 100000
limit3 = 100000


n = np.array([10, 50, 100, 500])
strategies = np.array(["Tau opt", "Random", "Call Me Once", "Learn New Secrets", "Token", "Spider", "Token improved", "Spider improved", "Math", "Bubble", "Call Min Secrets", "Call Max Secrets", "Call Best Secrets"])
values = np.array([[4, 6, 7, 9],[5.47, 9.13, 10.37, 13.09], [5.50, 9.13, 10.37, 13.11], [5.43, 9.14, 10.36, 13.09],[18.76, 95.35, 183.01, None], [18.96, 100.19, 182.54, None], [11.63, 31.28, 42.77, 680.78], [13.29, 35.65, 47.69, 702.72], [5.56, 9.25, 10.59, 13.36], [5.38, 8.91, 10.1, 12.81], [4.89, 8.58, 10.07, 13.03], [45.05, 902.46, None, None], [5.59, 12.02, 14.94, 21.56]])

forbidden = []

stratsToPlot = []

handles = []
# plt.yscale("log")
for i in range(len(strategies)):
    if strategies[i] not in forbidden and (values[i][0] == None or values[i][0] < limit0) and (values[i][1] == None or values[i][1] < limit1) and (values[i][2] == None or values[i][2] < limit2) and (values[i][3] == None or values[i][3] < limit3):
        stratsToPlot.append(strategies[i])
        plt.plot(n, values[i])
        handles.append(plt.scatter(n, values[i], label = strategies[i]))

font = {'family' : 'normal',
        'size'   : 20}

plt.rc('font', **font)    

plt.xlabel("n", fontsize = 20)
plt.ylabel("Tau", fontsize = 20)
plt.legend(stratsToPlot, handles = handles, loc='upper center', bbox_to_anchor=(1.1, 1))
plt.show()