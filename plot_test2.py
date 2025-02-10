import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets
from pyqtgraph.dockarea.Dock import Dock
from pyqtgraph.dockarea.DockArea import DockArea




class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, dark_mode=True):
        super().__init__()
        central_dock_area = DockArea()

        # create plot widget (and  dock)
        self.plot_widget = pg.PlotWidget()
        plot_dock = Dock(name="Plot Widget Dock", closable=True)
        plot_dock.addWidget(self.plot_widget)
        central_dock_area.addDock(plot_dock)

        
        self.setCentralWidget(central_dock_area)

        app = QtWidgets.QApplication.instance()
        

        

if __name__ == "__main__":
    pg.mkQApp()
    main = MainWindow(dark_mode=False)
    main.show()

    pg.exec()