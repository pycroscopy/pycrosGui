
#################################################################
#1######## Quantifit Main program
##
## Copyrigth Gerd Duscher

## Changes Nov 2012:
## Major Changes to python 3 and pyqt as GUI mashine
## change everything over to dictionary
## save and read dictionary file with pickle 
##
## Changes Jan 2013
## Minor bug fixes,
## reads SI files from Zeiss Libra
##
## Changes Feb 2013
## Include 'Results' Dictionary to output file
##
## Change April 2013
## Resolution Function Now a Product of two Lorentzians,
## Peakfit can select between Gaussians and Lorentzians
##
## Change May 2013
## Reads Camera Length and calculates collection angle for Libra,
## Images are now supported with deconvolution and probe calculation
## Working on averaging of spectra depending on scale of specific SI output
##
## Change June 2013
## Can use simulated LL as background for Quantifit
##
## Change December 2013
## Using pyqtgraph insteasd of Matplotlib to better support images and 3D
## and event handling. It's also faster.
##
## Changes May 2015 #0.974
## Added usage of XRPA cross section now: http://physics.nist.gov/PhysRefData/FFast/html/form.html
## Fixed bug with exposure time after selection of several spectra
## Added variety of background subtraction - Poly and Power only
##
## Changes Oct 2017 # 0.976
## Deleted maximum height in dialogs for high resolution screens
##
## Changes Oct 2017 # 0.977
## Switch to pyQt5, fixed bugs: Cursor, SI-quantifit, Quantifit-edge1 
##
#################################################################
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import os as os
import numpy as np
import scipy as scipy

import pyqtgraph as pg
import sys
sys.path.insert(0, '../pyTEMlib')

import pyTEMlib
print('pyTEMlib version :', pyTEMlib.__version__)
import pyTEMlib.file_tools

# =============================================================
#   Include Quantifit Libraries                                      #
# =============================================================
import sys
global frame
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
        # set additional capabilities
        self.InfoWidget = QDockWidget("Info ", self)
        self.InfoDialog = InfoDialog(self)
        self.InfoWidget.setFeatures(QDockWidget.DockWidgetMovable |
                              QDockWidget.DockWidgetFloatable)
        self.InfoWidget.setWidget(self.InfoDialog)# Add the dock to the main window
        
        self.addDockWidget(Qt.LeftDockWidgetArea, self.InfoWidget)
        self.tabifyDockWidget(self.DataWidget, self.InfoWidget)
        
        self.InfoWidget.visibilityChanged.connect(self.InfoDialog.updateInfo)

        self.LowLossWidget = QDockWidget("Low Loss ", self)
        self.LowLossDialog = LowLossDialog(self)
        self.LowLossWidget.setFeatures(QDockWidget.DockWidgetMovable |
                              QDockWidget.DockWidgetFloatable)
        self.LowLossWidget.setWidget(self.LowLossDialog)# Add the dock to the main window

        self.CoreLossWidget = QDockWidget("Core Loss ", self)
        self.CoreLossDialog = CoreLossDialog(self)
        self.CoreLossWidget.setFeatures(QDockWidget.DockWidgetMovable |
                              QDockWidget.DockWidgetFloatable)
        self.CoreLossWidget.setWidget(self.CoreLossDialog)# Add the dock to the main window
        
        
        self.PeakFitWidget = QDockWidget("Peak Fit", self)
        self.PeakFitDialog = PeakFitDialog(self)
        self.PeakFitWidget.setFeatures(QDockWidget.DockWidgetMovable |
                              QDockWidget.DockWidgetFloatable)
        self.PeakFitWidget.setWidget(self.PeakFitDialog)# Add the dock to the main window
        
        
        self.addDockWidget(Qt.LeftDockWidgetArea, self.LowLossWidget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.CoreLossWidget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.PeakFitWidget)
        
        self.tabifyDockWidget(self.InfoWidget, self.LowLossWidget)
        # self.tabifyDockWidget(self.QuantifitWidget, self.SimWidget)
        # self.tabifyDockWidget(self.QuantifitWidget, self.InfoWidget)
        self.tabifyDockWidget(self.LowLossWidget, self.CoreLossWidget)
        self.tabifyDockWidget(self.CoreLossWidget, self.PeakFitWidget, )
        
        self.LowLossWidget.visibilityChanged.connect(self.low_loss_update)
        self.CoreLossWidget.visibilityChanged.connect(self.core_loss_update)
        self.PeakFitWidget.visibilityChanged.connect(self.peak_fit_update)


    def plot_additional_features(self, plt):
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
            # self.plot_features = self.CoreLossDialog.additional_features()
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
    app=QApplication(args)
    f=MainWidget()        
    f.show()
    app.setStyle(QStyleFactory.create("Cleanlooks"))
    app.setPalette(QApplication.style().standardPalette())
    app.exec()


if __name__ == "__main__":
    # import sys
    main()  # sys.argv)
    
