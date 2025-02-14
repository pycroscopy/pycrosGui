
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
    
