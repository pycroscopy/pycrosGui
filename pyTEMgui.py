
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
from pyTEMGui.ProbeDialog import ProbeDialog
from pyTEMGui.AcquisitionDialog import AcquDialog
from pyTEMGui.MicroscopeDialog import MicroscopeDialog
# =======================================================================================================
#                                      Main Window Module                                               #
# =======================================================================================================

class MainWidget(BaseWidget):
    def __init__(self, filename=None):
        super().__init__(filename=filename)

        self.microscope = None
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

        self.ProbeDialog = ProbeDialog(self)
        self.ProbeWidget = self.add_sidebar(self.ProbeDialog)

        self.AcquDialog = AcquDialog(self)
        self.AcquWidget = self.add_sidebar(self.AcquDialog)

        self.MicroscopeDialog = MicroscopeDialog(self)
        self.MicroscopeWidget = self.add_sidebar(self.MicroscopeDialog)
                                                                             
        # ##### Add the docks to the main window ######                                                                         
        self.tabifyDockWidget(self.DataWidget, self.InfoWidget) 
        self.tabifyDockWidget(self.InfoWidget, self.LowLossWidget)
        self.tabifyDockWidget(self.LowLossWidget, self.CoreLossWidget)
        self.tabifyDockWidget(self.CoreLossWidget, self.PeakFitWidget)
        self.tabifyDockWidget(self.PeakFitWidget, self.ImageWidget)
        self.tabifyDockWidget(self.ImageWidget, self.AtomWidget)
        self.tabifyDockWidget( self.AtomWidget, self.ProbeWidget)
        self.tabifyDockWidget( self.ProbeWidget, self.AcquWidget)
        self.tabifyDockWidget(self.AcquWidget, self.MicroscopeWidget)
        
        # ##### Connect the visibility of the docks to the update function ###### 
        self.InfoWidget.visibilityChanged.connect(self.InfoDialog.updateInfo)
        self.LowLossWidget.visibilityChanged.connect(self.low_loss_update)
        self.CoreLossWidget.visibilityChanged.connect(self.core_loss_update)
        self.PeakFitWidget.visibilityChanged.connect(self.peak_fit_update)
        self.ImageWidget.visibilityChanged.connect(self.image_update)
        self.AtomWidget.visibilityChanged.connect(self.atom_update)
        self.ProbeWidget.visibilityChanged.connect(self.probe_update)
        
        
        self.LowLossWidget.setVisible(False)
        self.CoreLossWidget.setVisible(False)
        self.PeakFitWidget.setVisible(False)
        self.ImageWidget.setVisible(False)
        self.AtomWidget.setVisible(False)
        self.ProbeWidget.setVisible(False)
        
        self.DataWidget.raise_()
        
        #FView Sidebar groubs
        self.view.addSeparator()
        
        self.image_visible = QtWidgets.QAction('Image', self, checkable=True)
        self.image_visible.setShortcut('Ctrl+E')
        self.image_visible.setStatusTip('Togle image dialogs visbility')
        self.image_visible.toggled.connect(self.visible_image)
        self.view.addAction(self.image_visible)
        
        self.EELS_visible = QtWidgets.QAction('EELS', self, checkable=True)
        self.EELS_visible.setShortcut('Ctrl+E')
        self.EELS_visible.setStatusTip('Togle EELS dialogs visbility')
        self.EELS_visible.toggled.connect(self.visible_EELS)
        self.view.addAction(self.EELS_visible)
        
        EDS_visible = QtWidgets.QAction('EDS', self, checkable=True)
        EDS_visible.setShortcut('Ctrl+E')
        EDS_visible.setStatusTip('Togle EDS dialogs visbility')
        # EDS_visible.toggled.connect(self.visible_EDS)
        self.view.addAction(EDS_visible)
        
    def visible_EELS(self, checked):
        if checked:
            self.LowLossWidget.setVisible(True)
            self.CoreLossWidget.setVisible(True)
            self.PeakFitWidget.setVisible(True)
        else:
            self.LowLossWidget.setVisible(False)
            self.CoreLossWidget.setVisible(False)
            self.PeakFitWidget.setVisible(False)
            
            
    def visible_image(self, checked):
        if checked:
            self.ImageWidget.setVisible(True)
            self.AtomWidget.setVisible(True)
            self.ProbeWidget.setVisible(True)
        else:
            self.ImageWidget.setVisible(False)
            self.AtomWidget.setVisible(False)
            self.ProbeWidget.setVisible(False)
            
    def set_dataset(self):
        super().set_dataset()
        print(self.dataset.data_type.name)
        if 'SPEC' in self.dataset.data_type.name:
            self.EELS_visible.setChecked(True)
        elif 'IMAGE' in self.dataset.data_type.name :
            self.image_visible.setChecked(True)
        
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

    def probe_update(self, visible):
        if visible:
            self.ProbeDialog.update_sidebar()


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
    
