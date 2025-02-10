# -*- coding: utf-8 -*-
"""
Demonstrates basic use of LegendItem

"""

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui

plt = pg.plot(background='white')
plt.setWindowTitle('pyqtgraph example: Legend')
plt.addLegend()

c1 = plt.plot([0,1],[1,0] pen='r', name='red plot')
c2 = plt.plot([2,1,4,3], pen='b', fillLevel=0, fillBrush=(0,0,255,30), name='sp2')
c3 = plt.addLine(y=4, pen='g')

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QGuiApplication.instance().exec()