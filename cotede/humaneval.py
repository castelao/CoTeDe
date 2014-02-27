#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from numpy.random import permutation
import pylab
import matplotlib.pyplot as plt

from cotede.qc import ProfileQCCollection
from cotede.misc import combined_flag, adjust_anomaly_coefficients


class HumanQC(object):
    """
    """
    def __init__(self, x, z, baseflags=[], fails=[], doubt=[], refname=None):
        """
        """
        self.x = x
        self.z = z
        self.baseflags = baseflags
        self.fails = fails
        self.doubt = doubt
        self.refname = refname
        #self.redraw = True
        #while self.redraw:
        self.hgood_ind = []
        self.hbad_ind  = []
        self.hdoubt_ind  = []

        self.plot()

    def plot(self):
        """
        """
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot(self.x, self.z, 'b.',
                picker=10) # 5 points tolerance
        # Plot the bad ones
        self.ax.plot(self.x[self.baseflags==False],
                self.z[self.baseflags==False], 'r^')

        # Plot the dubious ones
        self.ax.plot(self.x[self.doubt==True],
                self.z[self.doubt==True], 'D',
                color='magenta')

        self.ax.plot(self.x[self.fails], self.z[self.fails], 'o', ms=12,
                alpha=0.4, color='cyan', visible=True)


        #line, = ax.plot(xs, ys, 'o', picker=5)  # 5 points tolerance
        self.selected, = self.ax.plot([self.x[0]], [self.z[0]], 'o', ms=12,
                alpha=0.4, color='yellow', visible=False)

        self.hbad, = self.ax.plot([], [], '^', ms=12,
                alpha=0.4, color='red', visible=True)
        self.hgood, = self.ax.plot([], [], 's', ms=12,
                alpha=0.4, color='green', visible=True)
        self.hdoubt, = self.ax.plot([], [], 'D', ms=12,
                alpha=0.4, color='magenta', visible=True)

        self.ax.set_ylabel('Pressure')
        self.ax.set_ylim(self.ax.get_ylim()[::-1])

        self.fig.canvas.mpl_connect('close_event', self.handle_close)
        self.fig.canvas.mpl_connect('pick_event', self.onpick)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        #pylab.connect('button_press_event', self.onpick)

        if self.refname is not None:
            self.ax.title(refname)

        pylab.show()

    def on_key(self, event):
        if (event.key == 'r') :
            #self.fig.canvas.draw()
            plt.close()
            self.plot()

        elif (event.key == 'c') :
            if self.dataind in self.hbad_ind:
                print "Removing %s from the bad list" % self.dataind
                self.hbad_ind.remove(self.dataind)
                self.hbad.set_data(self.x[self.hbad_ind],
                        self.z[self.hbad_ind])
                self.fig.canvas.draw()

            if self.dataind in self.hgood_ind:
                print "Removing %s from the good list" % self.dataind
                self.hgood_ind.remove(self.dataind)
                self.hgood.set_data(self.x[self.hgood_ind],
                        self.z[self.hgood_ind])
                self.fig.canvas.draw()

            if self.dataind in self.hdoubt_ind:
                print "Removing %s from the dubious list" % self.dataind
                self.hdoubt_ind.remove(self.dataind)
                self.hdoubt.set_data(self.x[self.hdoubt_ind],
                        self.z[self.hdoubt_ind])
                self.fig.canvas.draw()

        elif (event.key == 'f') :
            if self.dataind not in self.hbad_ind:
                print "Adding %s on the bad list" % self.dataind
                self.hbad_ind.append(self.dataind)
                self.hbad.set_data(self.x[self.hbad_ind], self.z[self.hbad_ind])
            if self.dataind in self.hgood_ind:
                print "Removing %s from the good list" % self.dataind
                self.hgood_ind.remove(self.dataind)
                self.hgood.set_data(self.x[self.hgood_ind], self.z[self.hgood_ind])
            self.fig.canvas.draw()

        elif (event.key == 't') :
            if self.dataind not in self.hgood_ind:
                print "Adding %s on the good list" % self.dataind
                self.hgood_ind.append(self.dataind)
                self.hgood.set_data(self.x[self.hgood_ind], self.z[self.hgood_ind])
            if self.dataind in self.hbad_ind:
                print "Removing %s from the bad list" % self.dataind
                self.hbad_ind.remove(self.dataind)
                self.hbad.set_data(self.x[self.hbad_ind], self.z[self.hbad_ind])
            self.fig.canvas.draw()

        elif (event.key == 'd') :
            if self.dataind not in self.hdoubt_ind:
                print "Adding %s on the dubious list" % self.dataind
                self.hdoubt_ind.append(self.dataind)
                self.hdoubt.set_data(self.x[self.hdoubt_ind], self.z[self.hdoubt_ind])
            self.fig.canvas.draw()

        elif (event.key == 'z') :
            (xini, xfin, zini, zfin) = self.ax.axis()
            xrange = xfin - xini
            yrange = zfin - zini
            #pylab.axis([xini, xfin, zini, zfin])
            self.ax.set_xlim(self.x[self.dataind] - xrange/2., 
                    self.x[self.dataind] + xrange/2.)
            self.ax.set_ylim(self.z[self.dataind] - yrange/2., 
                    self.z[self.dataind] + yrange/2.)
            self.fig.canvas.draw()

        elif (event.key == 'q') :
            print "Quiting."
            pylab.close()

    def onpick(self, event):
        """
        """
        if event.artist != self.line: return True

        N = len(event.ind)
        if not N: return True

        # the click locations
        x = event.mouseevent.xdata
        y = event.mouseevent.ydata

        distances = np.hypot(x-self.x[event.ind], y-self.z[event.ind])
        indmin = distances.argmin()
        self.dataind = event.ind[indmin]

        self.selected.set_visible(True)
        self.selected.set_data(self.x[self.dataind], self.z[self.dataind])
        #pylab.plot(self.x[dataind], self.z[dataind], 'r^')
        self.fig.canvas.draw()

    def handle_close(self, event):
        print('Closed Figure!')
        print "Good list: %s" % self.hgood_ind
        print "Bad list: %s" % self.hbad_ind
        print "Doubt list: %s" % self.hdoubt_ind
