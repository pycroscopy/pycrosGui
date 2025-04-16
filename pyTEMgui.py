
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
# Image and Atoms dialogs work on images.
#################################################################
from PyQt5 import QtCore
from PyQt5 import QtWidgets

import PyQt5
import sys
sys.path.insert(0, '../pyTEMlib/')
import pyTEMlib

import numpy as np

import pyqtgraph as pg

# =============================================================
#   Include pycroscopy Libraries                                      #
# =============================================================

# =============================================================
#   Include pycroscopy Dialogs                                      #
# =============================================================

from pycrosGui.BaseWidget import BaseWidget

from pyTEMGui.InfoDialog import InfoDialog
from pyTEMGui.LowLossDialog import LowLossDialog
from pyTEMGui.CoreLossDialog import CoreLossDialog
from pyTEMGui.PeakFitDialog import PeakFitDialog
from pyTEMGui.ImageDialog import ImageDialog
from pyTEMGui.AtomDialog import AtomDialog
from pyTEMGui.AcquisitionDialog import AcquDialog
# =======================================================================================================
#                                      Main Window Module                                               #
# =======================================================================================================

class MainWidget(BaseWidget):
    def __init__(self, filename=None):
        super().__init__(filename=filename)
        
        # ##### Add dialogs with additional capabilities                                                        
        self.InfoDialog = InfoDialog(self)
        self.InfoWidget = self.add_sidebar(self.InfoDialog)
                                                                           
        self.LowLossDialog = LowLossDialog(self)
        self.LowLossWidget = self.add_sidebar(self.LowLossDialog)# Add the dock to the main window                                                                     
        
        self.CoreLossDialog = CoreLossDialog(self)
        self.CoreLossWidget = self.add_sidebar(self.CoreLossDialog)# Add the dock to the main window
        
        self.PeakFitDialog = PeakFitDialog(self)
        self.PeakFitWidget = self.add_sidebar(self.PeakFitDialog)# Add the dock to the main window
                                                             
        self.ImageDialog = ImageDialog(self)
        self.ImageWidget = self.add_sidebar(self.ImageDialog)# Add the dock to the main window
        
        self.AtomDialog = AtomDialog(self)
        self.AtomWidget = self.add_sidebar(self.AtomDialog)
        
        self.AcquDialog = AcquDialog(self)
        self.AcquWidget = self.add_sidebar(self.AcquDialog)
                                                                             
        # ##### Add the docks to the main window ######                                                                         
        self.tabifyDockWidget(self.DataWidget, self.InfoWidget) 
        self.tabifyDockWidget(self.InfoWidget, self.LowLossWidget)
        self.tabifyDockWidget(self.LowLossWidget, self.CoreLossWidget)
        self.tabifyDockWidget(self.CoreLossWidget, self.PeakFitWidget)
        self.tabifyDockWidget(self.PeakFitWidget, self.ImageWidget)
        self.tabifyDockWidget(self.ImageWidget, self.AtomWidget)
        self.tabifyDockWidget( self.AtomWidget, self.AcquWidget)
        
        # ##### Connect the visibility of the docks to the update function ###### 
        self.InfoWidget.visibilityChanged.connect(self.InfoDialog.updateInfo)
        self.LowLossWidget.visibilityChanged.connect(self.low_loss_update)
        self.CoreLossWidget.visibilityChanged.connect(self.core_loss_update)
        self.PeakFitWidget.visibilityChanged.connect(self.peak_fit_update)
        self.ImageWidget.visibilityChanged.connect(self.image_update)
        self.AtomWidget.visibilityChanged.connect(self.atom_update)
        
        self.DataWidget.raise_()


    def plot_additional_features(self, plt):
        """
        Adds additional features to the plot, as defined in the dialogs.
        The current dialog is determined by the metadata of the dataset.

        """
        super().plot_additional_features(plt)
        if 'SPEC' in self.dataset.data_type.name:
            ene = np.array(self.dataset.get_spectral_dims(return_axis=True)[0])
            energy_scale = np.append(ene, ene[-1])
        
        additional_features = {}
        if 'additional_features' not in self.dataset.metadata['plot']:
            pass
        elif 'Image' in self.dataset.metadata['plot']['additional_features']:
                additional_features = self.ImageDialog.get_additional_features()
                if 'atoms' in additional_features:
                    self.blobs.setData(pos=additional_features['atoms'])
                    self.blobs.setVisible(True)
                    del additional_features['atoms']
                else:
                    self.blobs.setData(pos=[[0,0]])
                    self.blobs.setVisible(False)
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

    # ##### Update functions for the dialogs ######
    def low_loss_update(self, visible):
        if visible:
            self.LowLossDialog.update_ll_sidebar()

    def core_loss_update(self, visible):
        if visible:
            self.CoreLossDialog.update_cl_sidebar()
    
    def peak_fit_update(self, visible):
        if visible:
            self.PeakFitDialog.update_peak_sidebar()
    
    def image_update(self, visible):
        if visible:
            self.ImageDialog.update_sidebar()

    def atom_update(self, visible):
        if visible:
            self.AtomDialog.update_sidebar()


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
    
