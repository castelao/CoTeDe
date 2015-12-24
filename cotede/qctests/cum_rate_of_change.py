# -*- coding: utf-8 -*-

"""

    Based on Timms 2011, p9597

"The first case in Equation (1) ensures that the cumulative rate of change function is able to quickly respond to degradations in sensor quality, while the second case ensures that it takes a longer time for confidence to return in the measurements from that sensor once the rate of change of the parameter decreases." (Timms 2011)

        Small   S->M            Medium          M->L            Large
Temp    <0.03   0.03 to 0.05    0.05 to 0.07    0.07 to 0.11    >0.11
Cond    <50     50 to 100       100 to 150      150 to 250      >250


Timms 2011 uses k=0.8

if (RoC_small (t) + 0.5 × RoC_medium (t)) < (cRoC_small (t - 1) + 0.5 × cRoC_medium (t - 1)):
    cRoC_i (t) = RoC_i (t)
else
    cRoC_i (t) = (1 - k) × RoC_i(t) + k * cRoC_i(t - 1)

i = small, medium, large
"""

from numpy import ma

def cum_rate_of_change(data, v, memory):

    output = ma.masked_all_like(data[v])
    output[1:] = ma.absolute(ma.diff(data[v]))

    for i in range(2, output.size):
        if output[i] < output[i-1]:
            output[i] = (1 - memory) * output[i] + memory * output[i-1]

    return output
