# This is a simple pseudo-random number generator
import math


def pseduo_random_even(A,M,n,x0):
    re = []
    re.append(x0)
    for i in range(1,n):
        re.append(A*re[i-1]%M)
    for i in range(n):
         re[i]/=M
    return re


def LCG(n,x0):
    re = []
    re.append(x0)
    for i in range(1, n):
        re.append((314159269 * re[i - 1] + 453806245) % (2**31))
    for i in range(n):
         re[i] /= (2**31)
    return re

def pseduo_random_negative_exponential_distribution(la,n,x0):
    res = LCG(n,x0)
    for i in range(n):
        res[i] = -1/la*(math.log(res[i],math.e))
    return res

# x = pseduo_random_even(3,2**30-1,10**5,31)
# y = pseduo_random_even(3,2**30-1,10**5,47)

# x = LCG(10**5,31)
# y = LCG(10**5,159269)

# x = pseduo_random_negative_exponential_distribution(31,10**5,31)
# y = pseduo_random_negative_exponential_distribution(31,10**5,159269)

# plt.figure(figsize=(1, 1), dpi=100)
# plt.scatter(x, y, s = 0.1)
# plt.show()