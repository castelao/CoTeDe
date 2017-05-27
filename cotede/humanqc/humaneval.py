# -*- coding: utf-8 -*-

""" Procedures for visual inspection and human flagging.
"""

import numpy as np
from numpy import ma

try:
    import pylab
    import matplotlib.pyplot as plt
except:
    print('matplotlib is not available')


class HumanQC(object):
    """ Plot a profile and collect human QC evaluation

        Still have much to improve here.
    """
    def __init__(self):
        pass

    def eval(self, x, z, baseflag=None, fails=None,
            humanflag=None, refname=None, clim=None):
        """
        """
        self.x = np.asanyarray(x)
        self.z = np.asanyarray(z)
        self.clim = clim

        assert x.shape == z.shape, "Data and z coordinate must have same shape"

        if baseflag is None:
            self.baseflag = ma.ones(x.size).astype('bool')
        else:
            self.baseflag = np.asanyarray(baseflag)
            assert self.baseflag.shape == self.x.shape

        if humanflag is None:
            self.humanflag = ma.masked_all(self.x.size,
                    dtype='object')
        else:
            self.humanflag = np.asanyarray(humanflag)
            assert self.baseflag.shape == self.x.shape

        if fails is None:
            self.fails = ma.zeros(x.size).astype('bool')
        else:
            self.fails = np.asanyarray(fails)
            assert self.fails.shape == self.x.shape

        self.refname = refname

        self.plot()
        return self.humanflag

    def plot(self):
        """
        """
        self.fig, self.ax = plt.subplots()
        try:
            self.ax.fill_betweenx(self.clim['z'],
                    self.clim['mn'] - 6*self.clim['std'],
                    self.clim['mn'] + 6*self.clim['std'],
                    color='r', alpha=0.2)
            self.ax.fill_betweenx(self.clim['z'],
                    self.clim['mn'] - 3*self.clim['std'],
                    self.clim['mn'] + 3*self.clim['std'],
                    color='g', alpha=0.2)
        except:
            print("Wasn't able to plot climatology")
        self.line, = self.ax.plot(self.x, self.z, 'b.',
                picker=10) # 5 points tolerance
        # Plot the bad ones
        self.ax.plot(self.x[self.baseflag==False],
                self.z[self.baseflag==False], 'r^')

        # Plot the dubious ones
        self.ax.plot(
                self.x[self.humanflag=='doubt'],
                self.z[self.humanflag=='doubt'],
                'D', color='magenta')

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


    def draw_humanflags(self, ind, flag):
        assert flag in [None, 'good', 'bad', 'doubt']

        if flag is None:
            self.humanflag.mask[self.dataind] = True
        else:
            self.humanflag[ind] = flag

        self.hbad.set_data(
                self.x[self.humanflag=='bad'],
                self.z[self.humanflag=='bad'])
        self.hgood.set_data(
                self.x[self.humanflag=='good'],
                self.z[self.humanflag=='good'])
        self.hdoubt.set_data(
                self.x[self.humanflag=='doubt'],
                self.z[self.humanflag=='doubt'])
        self.fig.canvas.draw()

    def on_key(self, event):
        if (event.key == 'r') :
            #self.fig.canvas.draw()
            plt.close()
            self.plot()

        elif (event.key == 'c') :
            print("Removing %s from the human list" % self.dataind)
            self.draw_humanflags(self.dataind, None)

        elif (event.key == 'f') :
            print("Adding %s on the bad list" % self.dataind)
            self.draw_humanflags(self.dataind, 'bad')

        elif (event.key == 't') :
            print("Adding %s on the good list" % self.dataind)
            self.draw_humanflags(self.dataind, 'good')

        elif (event.key == 'd') :
            print("Adding %s on the dubious list" % self.dataind)
            self.draw_humanflags(self.dataind, 'doubt')

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
            print("Quiting.")
            pylab.close()

    def onpick(self, event):
        """
        """
        if event.artist != self.line: return True

        N = len(event.ind)
        if not N: return True

        if N == 1:
            self.dataind = event.ind
        else:
            # Will get the closest point
            x = event.mouseevent.xdata
            y = event.mouseevent.ydata

            distances = np.hypot(x-self.x[event.ind], y-self.z[event.ind])
            indmin = distances.argmin()
            self.dataind = event.ind[indmin]

        self.selected.set_visible(True)
        self.selected.set_data(self.x[self.dataind], self.z[self.dataind])
        self.fig.canvas.draw()

    def handle_close(self, event):
        print('Closed Figure!')
        print("Good list: %s" % np.nonzero(self.humanflag=='good')[0])
        print("Bad list: %s" % np.nonzero(self.humanflag=='bad')[0])
        print("Doubt list: %s" % np.nonzero(self.humanflag=='doubt')[0])
