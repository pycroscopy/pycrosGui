
# ################################################################
# 1######## pyTEMgui Main program
# #
# # by Gerd Duscher

# # Started February 2025:
# # Also used as an example for pycrosGUI
# #
# BaseWIdget with 
# InfoWidget which changes with imae or spectrum file.
# LowLoss, CoreLoss, and PeakFit dialogs work on spectra and spectral images
#
#################################################################
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import PyQt5

import os as os
import numpy as np
import scipy as scipy

import pyqtgraph as pg

# =============================================================
#   Include Quantifit Libraries                                      #
# =============================================================
# global frame  
import sidpy

from BaseWidget import BaseWidget
from InfoDialog import InfoDialog
from LowLossDialog import LowLossDialog
from CoreLossDialog import CoreLossDialog
from PeakFitDialog import PeakFitDialog


# =======================================================================================================
#                                      Main Window Module                                               #
# =======================================================================================================


class MainWidget(BaseWidget):
    def __init__(self, filename=None):
        super().__init__(filename=filename)
        
        # add dialogs with additional capabilities 
        self.InfoWidget = PyQt5.QtWidgets.QDockWidget("Info ", self)
        self.InfoDialog = InfoDialog(self)
        self.InfoWidget.setFeatures(PyQt5.QtWidgets.QDockWidget.DockWidgetMovable |
                              PyQt5.QtWidgets.QDockWidget.DockWidgetFloatable)
        self.InfoWidget.setWidget(self.InfoDialog)# Add the dock to the main window
        self.addDockWidget (QtCore.Qt.LeftDockWidgetArea, self.InfoWidget)
        self.tabifyDockWidget(self.DataWidget, self.InfoWidget) 
        self.InfoWidget.visibilityChanged.connect(self.InfoDialog.updateInfo)

        self.LowLossWidget = PyQt5.QtWidgets.QDockWidget("Low Loss ", self)
        self.LowLossDialog = LowLossDialog(self)
        self.LowLossWidget.setFeatures(PyQt5.QtWidgets.QDockWidget.DockWidgetMovable |
                              PyQt5.QtWidgets.QDockWidget.DockWidgetFloatable)
        self.LowLossWidget.setWidget(self.LowLossDialog)# Add the dock to the main window

        self.CoreLossWidget = PyQt5.QtWidgets.QDockWidget("Core Loss ", self)
        self.CoreLossDialog = CoreLossDialog(self)
        self.CoreLossWidget.setFeatures(PyQt5.QtWidgets.QDockWidget.DockWidgetMovable |
                              PyQt5.QtWidgets.QDockWidget.DockWidgetFloatable)
        self.CoreLossWidget.setWidget(self.CoreLossDialog)# Add the dock to the main window
        
        self.PeakFitWidget = PyQt5.QtWidgets.QDockWidget("Peak Fit", self)
        self.PeakFitDialog = PeakFitDialog(self)
        self.PeakFitWidget.setFeatures(PyQt5.QtWidgets.QDockWidget.DockWidgetMovable |
                              PyQt5.QtWidgets.QDockWidget.DockWidgetFloatable)
        self.PeakFitWidget.setWidget(self.PeakFitDialog)# Add the dock to the main window
        
        self.addDockWidget (QtCore.Qt.LeftDockWidgetArea, self.LowLossWidget)
        self.addDockWidget (QtCore.Qt.LeftDockWidgetArea, self.CoreLossWidget)
        self.addDockWidget (QtCore.Qt.LeftDockWidgetArea, self.PeakFitWidget)
        
        self.tabifyDockWidget(self.InfoWidget, self.LowLossWidget)
        self.tabifyDockWidget(self.LowLossWidget, self.CoreLossWidget)
        self.tabifyDockWidget(self.CoreLossWidget, self.PeakFitWidget, )
        
        self.LowLossWidget.visibilityChanged.connect(self.low_loss_update)
        self.CoreLossWidget.visibilityChanged.connect(self.core_loss_update)
        self.PeakFitWidget.visibilityChanged.connect(self.peak_fit_update)

        self.DataWidget.raise_()

    def plot_additional_features(self, plt):
        """
        Adds additional features to the plot, as defined in the dialogs.
        The current dialog is determined by the metadata of the dataset.

        """
        super().plot_additional_features(plt)
        ene = np.array(self.dataset.get_spectral_dims(return_axis=True)[0])
        energy_scale = np.append(ene, ene[-1])
        
        additional_features = {}
        if 'additional_features' not in self.dataset.metadata['plot']:
           pass
        elif 'LowLoss' in self.dataset.metadata['plot']['additional_features']:
            additional_features = self.LowLossDialog.get_additional_features()
        elif 'CoreLoss' in self.dataset.metadata['plot']['additional_features']:
            additional_features = self.CoreLossDialog.get_additional_features()
            self.plot_features = additional_features
        elif 'PeakFit' in self.dataset.metadata['plot']['additional_features']:
            additional_features = self.PeakFitDialog.get_additional_features()
        
        additional_spectra = {}
        if 'additional_spectra' not in self.dataset.metadata['plot']:
            pass
        elif 'LowLoss' in self.dataset.metadata['plot']['additional_spectra']:
            additional_spectra = self.LowLossDialog.get_additional_spectra()
        elif 'CoreLoss' in self.dataset.metadata['plot']['additional_spectra']:
            additional_spectra = self.CoreLossDialog.get_additional_spectra()
        elif 'PeakFit' in self.dataset.metadata['plot']['additional_spectra']:
            print('peak add')
            additional_spectra = self.PeakFitDialog.get_additional_spectra()
        
        colors = ('red', 'green', 'orange', 'purple', 'cyan', 'magenta', 'grey', 'lightgrey', 'black','black')
        for i, key in enumerate(additional_spectra.keys()):
            spectrum = additional_spectra[key]*self.intensity_scale
            curve = pg.PlotCurveItem(np.array(energy_scale), spectrum, 
                                     pen = colors[i%10], stepMode=True,
                                     padding = 0, name=key) #, name=memtags['name'])
            plt.addItem(curve)
            curve.setPen(pg.mkPen(colors[i%10], width=2))
        for key, item in additional_features.items():
            plt.addItem(item)

    
    def low_loss_update(self, visible):
        if visible:
            self.LowLossDialog.update_ll_sidebar()

    def core_loss_update(self, visible):
        if visible:
            self.CoreLossDialog.update_cl_sidebar()
    
    def peak_fit_update(self, visible):
        if visible:
            self.PeakFitDialog.update_peak_sidebar()


def main(args=[]):
    global app
    app=QtWidgets.QApplication(args)
    f=MainWidget()        
    f.show()
    app.setStyle(QtWidgets.QStyleFactory.create("Cleanlooks"))
    app.setPalette(QtWidgets.QApplication.style().standardPalette())
    app.exec()


if __name__ == "__main__":
    # import sys
    main()  # sys.argv)
    
