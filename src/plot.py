import numpy as np 
import matplotlib.pyplot as plt
import pandas as pd

limit0 = 100
limit1 = 1300
limit2 = 1300
limit3 = 2500


n = np.array([10, 50, 100, 500])
strategies = np.array(["Tau opt", "Random", "Call Me Once", "Learn New Secrets", "Token", "Spider", "Token improved", "Spider improved", "Math", "Bubble", "Call Min Secrets", "Call Max Secrets", "Call Best Secrets"])
values = np.array([[4, 6, 7, 9],[5.47, 9.13, 10.37, 13.09], [5.50, 9.13, None, None], [4.67, 8.72, 10.02, 13.0],[18.76, 95.35, 183.01, None], [18.96, 100.19, 182.54, None], [11.63, 31.28, 42.77, None], [13.29, 35.65, 47.69, None], [5.56, 9.25, 10.59, 13.36], [5.38, 8.91, 10.1, 12.81], [4.89, 8.58, 10.07, 13.03], [45.05, 902.46, None, None], [5.59, 12.02, 14.94, None]])

forbidden = []

stratsToPlot = []

for i in range(len(strategies)):
    if strategies[i] not in forbidden and (values[i][0] == None or values[i][0] < limit0) and (values[i][1] == None or values[i][1] < limit1) and (values[i][2] == None or values[i][2] < limit2) and (values[i][3] == None or values[i][3] < limit3):
        stratsToPlot.append(strategies[i])
        plt.plot(n, values[i])

font = {'family' : 'normal',
        'size'   : 18}

plt.rc('font', **font)    

plt.xlabel("n", fontsize = 20)
plt.ylabel("Tau", fontsize = 20)
plt.legend(stratsToPlot)
plt.show()