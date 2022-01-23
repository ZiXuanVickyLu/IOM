# This is a simple pseudo-random number generator
import math


def LCG(n,x0):
    re = []
    re.append(x0)
    for i in range(1, n):
        re.append((314159269 * re[i - 1] + 453806245) % (2**31))
    for i in range(n):
         re[i] /= (2**31)
    return re

