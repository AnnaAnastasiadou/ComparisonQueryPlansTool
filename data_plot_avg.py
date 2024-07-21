import matplotlib.pyplot as plt
from scipy.stats import pearsonr
import numpy as np
from statsmodels.nonparametric.smoothers_lowess import lowess

data = [
    ['12.sql', 0, 136.82766666666657],
    ['18.sql', 0, 116.71033333333337],
    ['16.sql', 1, 166.64466666666667],
    ['4.sql', 0, 0.02],
    ['7.sql', 0, 90.1653333333333],
    ['1.sql', 0, 943.5073333333333],
    ['10.sql', 0, 167.11066666666662],
    ['15.sql', 5, 420.69900000000007],
    ['22.sql', 0, 20.80966666666666],
    ['5.sql', 0, 89.51099999999997],
    ['19.sql', 0, 10.767333333333335],
    ['14.sql', 0, 5.3856666666666415],
    ['13.sql', 0, 79.74433333333324],
    ['2.sql', 6, 75.183],
    ['17.sql', 0, 22.474333333333373],
    ['9.sql', 14, 254.58300000000008],
    ['20.sql', 8, 538.3053333333334],
    ['11.sql', 10, 11.185333333333338],
    ['8.sql', 0, 193.9320000000001],
    ['3.sql', 3, 38.93966666666662],
    ['21.sql', 4, 90.78033333333337],
    ['6.sql', 0, 248.73599999999996],
    ['9b.sql', 12, 2261.392333333333],
    ['28c.sql', 9, 224.44799999999987],
    ['2d.sql', 0, 29.907],
    ['9c.sql', 10, 3005.7496666666666],
    ['5a.sql', 7, 58.64266666666666],
    ['29b.sql', 34, 2344.5963333333334],
    ['17f.sql', 0, 286.6826666666657],
    ['33b.sql', 24, 75.34733333333334],
    ['11d.sql', 8, 76.91833333333334],
    ['19a.sql', 18, 4450.2953333333335],
    ['21c.sql', 13, 6.316333333333333],
    ['25c.sql', 0, 609.5293333333339],
    ['2c.sql', 0, 27.311999999999994],
    ['10b.sql', 0, 15.571333333333333],
    ['31b.sql', 16, 265.7706666666666],
    ['33c.sql', 20, 134.84066666666666],
    ['23b.sql', 5, 6.371000000000009],
    ['2b.sql', 0, 21.68866666666666],
    ['14a.sql', 0, 37.661333333333346],
    ['7a.sql', 4, 38.00066666666669],
    ['16a.sql', 0, 12.84566666666666],
    ['11c.sql', 12, 78.04533333333333],
    ['8a.sql', 3, 164.36366666666663],
    ['2a.sql', 0, 22.74933333333335],
    ['12b.sql', 11, 0.18133333333333335],
    ['15d.sql', 20, 1408.3226666666667],
    ['15b.sql', 11, 5.5646666666666675],
    ['3c.sql', 11, 2905.333666666667],
    ['23a.sql', 5, 7.74133333333332],
    ['24b.sql', 2, 4.6766666666666685],
    ['12c.sql', 0, 117.96166666666666],
    ['27c.sql', 21, 10.158000000000001],
    ['18a.sql', 13, 22668.173],
    ['22a.sql', 0, 111.18533333333336],
    ['16c.sql', 0, 32.99966666666668],
    ['13b.sql', 10, 24.91933333333331],
    ['1c.sql', 3, 1.2046666666666666],
    ['16d.sql', 0, 66.925],
    ['4c.sql', 10, 1365.7600000000002],
    ['9d.sql', 0, 973.6283333333331],
    ['17e.sql', 0, 297.83733333333294],
    ['5c.sql', 0, 65.65366666666667],
    ['11b.sql', 13, 40.10366666666667],
    ['11a.sql', 16, 8.278333333333332],
    ['10c.sql', 15, 574.1596666666665],
    ['26b.sql', 16, 1023.686],
    ['26a.sql', 19, 14069.784999999998],
    ['21b.sql', 18, 8.104333333333333],
    ['31a.sql', 10, 9273.348666666667],
    ['27a.sql', 19, 56.839],
    ['20b.sql', 9, 37913.47066666667],
    ['14c.sql', 0, 158.7106666666667],
    ['18c.sql', 11, 635.894666666667],
    ['19c.sql', 16, 9701.852333333334],
    ['4a.sql', 10, 968.9139999999999],
    ['3a.sql', 11, 4909.857333333333],
    ['13d.sql', 0, 111.77366666666678],
    ['18b.sql', 7, 436.0366666666667],
    ['6a.sql', 0, 2.7863333333333338],
    ['24a.sql', 14, 127.55066666666664],
    ['26c.sql', 18, 54773.63766666667],
    ['22c.sql', 0, 863.9553333333333],
    ['1a.sql', 3, 1.12],
    ['30c.sql', 8, 1641.405],
    ['8d.sql', 12, 383.8816666666665],
    ['25a.sql', 0, 298.0376666666666],
    ['17d.sql', 5, 1021.0796666666671],
    ['22d.sql', 0, 434.9176666666667],
    ['8c.sql', 12, 3222.585333333333],
    ['16b.sql', 0, 953.64],
    ['28a.sql', 15, 1212.4323333333334],
    ['21a.sql', 18, 60.55599999999999],
    ['3b.sql', 6, 1453.731],
    ['31c.sql', 13, 9113.560333333333],
    ['15a.sql', 16, 1126.31],
    ['17c.sql', 5, 473.28933333333407],
    ['8b.sql', 8, 67.89066666666668],
    ['12a.sql', 0, 59.74099999999999],
    ['25b.sql', 9, 209.64300000000003],
    ['32b.sql', 3, 6.5103333333333255],
    ['32a.sql', 3, 5.005666666666666],
    ['20c.sql', 9, 38854.63333333334],
    ['27b.sql', 23, 68.86099999999999],
    ['15c.sql', 20, 1999.834],
    ['17a.sql', 0, 361.5526666666671],
    ['4b.sql', 9, 31.455666666666662],
    ['19b.sql', 22, 1843.6153333333332],
    ['7b.sql', 4, 54.959],
    ['6b.sql', 0, 45.362],
    ['7c.sql', 15, 8831.974333333334],
    ['33a.sql', 7, 9.426666666666666],
    ['1d.sql', 0, 0.082],
    ['1b.sql', 0, 0.025333333333333347],
    ['28b.sql', 13, 2004.8329999999999],
    ['6c.sql', 0, 2.9426666666666663],
    ['23c.sql', 5, 21.65366666666667],
    ['14b.sql', 5, 7.821333333333333],
    ['29a.sql', 35, 114.44633333333333],
    ['6f.sql', 0, 171.869],
    ['17b.sql', 4, 110.1843333333339],
    ['30a.sql', 0, 92.01100000000001],
    ['22b.sql', 0, 16.783666666666686],
    ['29c.sql', 35, 2847.461],
    ['13a.sql', 0, 32.33399999999983],
    ['6d.sql', 0, 190.12866666666682],
    ['5b.sql', 5, 40.11466666666667],
    ['9a.sql', 14, 3170.308333333334],
    ['6e.sql', 0, 3.7023333333333333],
    ['10a.sql', 4, 42.93133333333333],
    ['30b.sql', 4, 4.852666666666664],
    ['20a.sql', 9, 81162.56866666666],
    ['13c.sql', 10, 72.56633333333332]
]

xs = [d[1] for d in data]
ys = [d[2] for d in data]

# plt.scatter(xs, ys)

from scipy.stats import pearsonr


# remove outliers
import numpy as np
xs = np.array(xs)
ys = np.array(ys)
mean_x = np.mean(xs)
mean_y = np.mean(ys)
std_x = np.std(xs)
std_y = np.std(ys)

xxs = []
yys = []
for i in range(len(ys)):
    if np.abs(ys[i] - mean_y) < 2.0 * std_y:
        xxs.append(xs[i])
        yys.append(ys[i])
    else:
        print(f"aaaaa: {xs[i],ys[i]}")
        # plt.plot(xs[i],ys[i],'rx')

xs = xxs
ys = yys
corr, _ = pearsonr(xs, ys)
print('Pearsons correlation: %.3f' % corr)

# Lowess smoothing
# lowess_smoothed = lowess(ys, xs, frac=0.3)

#line of best fit
import numpy as np
m, b = np.polyfit(xs, ys, 1)
plt.scatter(xs, ys)
plt.plot(xs, m*np.array(xs) + b, color='red')
# plt.plot(lowess_smoothed[:, 0], lowess_smoothed[:, 1], color='green')
plt.xlabel("Tree Edit Distance")
plt.ylabel("Time Execution Difference (ms)")
plt.legend(['Data Points','Line of Best Fit ', 'Lowess Curve'])
plt.savefig("BestFit.png")
# plt.savefig("TrendCapture.png")
plt.show()
