import numpy as np

data = np.loadtxt('rule_power.txt',dtype='float',delimiter=',')
data = data.tolist()
d = []
d.append(data)
d.append(data)
print((np.array(d)).shape)
print d
