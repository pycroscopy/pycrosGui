
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
import pyTEMlib.file_tools

# =============================================================
#   Include Quantifit Libraries                                      #
# =============================================================
import sys
global frame
import sidpy
from InfoDialog import InfoDialog
from DataDialog import DataDialog

# =======================================================================================================
#                                      Main Window Module                                               #
# =======================================================================================================


class MainWidget(QMainWindow):    
    def __init__(self):
        super().__init__()
        self.version = '2025-1-1'
        
        self.dataset_list = ['None']
        self.image_list = ['Sum']
        self.dir_name = pyTEMlib.file_tools.get_last_path()

        self.key = None
        self.new_info = False
        self.image = 'Sum'
        self.main = ""
        self.cursor = None
        self.intensity_scale = 1
  
        self.save_path = True

        if not os.path.isdir(self.dir_name):
            self.dir_name = '.'

        self.extensions = '*'
        self.file_name = ''
        self.datasets = {}
        self.dataset = None
        self.sd0 = 0
        self.sds = 0

        self.bin_x = 0
        self.bin_y = 0
        

        self.start_channel = -1
        self.end_channel = -2
        QMainWindow.__init__(self)
        
        self.path = '.'
        self.setWindowTitle('Quantifit version '+str(self.version) +'qt serial #: 1')
        self.add_spectrum = []
        self.statusBar()
        self.tabCurrent = 1
        #============================================================================
        #=============== Definition of the Main Window LayOut =======================
        #============================================================================
        # Widget that contains the Plot and toolbar
        centralWidget = QWidget ()
        self.centralWidget = centralWidget
        
        #============= Definition of Figure and Dialog Windows  for Parameters =================

        self.height = 450
        screen = QDesktopWidget().screenGeometry()
        self.height = screen.height() 
        self.width = screen.width() 
	        
        ## Switch to using white background and black foreground
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        # Creating an instance of the Figure
        self.plotParamWindow  = pg.PlotWidget()
        self.plotParamWindow2 = pg.PlotWidget()
        self.plotParamWindow3 = pg.ImageView()

        self.plotParamWindow.plot((0,1),(0,1))

        plotLayout  = QVBoxLayout()
        plotLayout1 = QVBoxLayout()
        plotLayout2 = QVBoxLayout()
        plotLayout3 = QVBoxLayout()

        validfloat = QDoubleValidator()
        top_layout = QHBoxLayout()
        self.left_cursor_label = QLabel("Cursor Start")
        self.left_cursor_value = QLineEdit(" 100.0")
        self.left_cursor_value.setValidator(validfloat)
        top_layout.addWidget(self.left_cursor_label)
        top_layout.addWidget(self.left_cursor_value)
        self.right_cursor_label = QLabel("End")
        self.right_cursor_value = QLineEdit(" 100.0")
        self.right_cursor_value.setValidator(validfloat)
        top_layout.addWidget(self.right_cursor_label)
        top_layout.addWidget(self.right_cursor_value)
        
        top_widget = QWidget()
        top_widget.setLayout(top_layout)
        self.plot1 = QWidget()

        plotLayout1.addWidget(top_widget)        
        plotLayout1.addWidget(self.plotParamWindow)        
        self.plot1.setLayout(plotLayout1)

        plot2 = QWidget()
        plotLayout2.addWidget(self.plotParamWindow2)        
        plot2.setLayout(plotLayout2)

        self.plot3 = QWidget()
        plotLayout3.addWidget(self.plotParamWindow3)        
        self.plot3.setLayout(plotLayout3)
        
        self.tab = QTabWidget()
        self.tab.addTab(self.plot1, 'Spectrum')
        self.tab.addTab(plot2, 'PeakFit')
        self.tab.addTab(self.plot3, 'Image')
        self.tab.currentChanged[int].connect(self.updateTab)
        self.tab.setTabsClosable(True)
        self.tab.tabCloseRequested.connect(self.onTabClose)
        
        #self.tab.setTabIcon (0, QIcon(Empty))        
        plotLayout.addWidget(self.tab)
        
        self.status =  self.statusBar() #QStatusBar()
        self.status.showMessage(" No data")
        #plotLayout.addWidget(self.status)
        
        # Adding the layout to the widget 
        centralWidget.setLayout(plotLayout)
        # Making that Widget the central widget for the window
        self.setCentralWidget(centralWidget)
        #self.tabifiedDockWidgets(centralWidget)
        
        #============= Definition Left QDialog  =================
        # 
        #        Definition of the Dock Widget:         
        #  that works as a container for the dialog widget
        
        self.DataWidget = QDockWidget("Datasets ", self)
        self.DataDialog = DataDialog(self)
        
        self.DataWidget.setWidget(self.DataDialog)# Add the dock to the main window
        #self.addDockWidget(Qt.LeftDockWidgetArea, LeftDockWidget)
        #
        self.addDockWidget(Qt.LeftDockWidgetArea, self.DataWidget)
        
        self.InfoWidget = QDockWidget("Info ", self)
        self.InfoDialog = InfoDialog(self)
        self.InfoWidget.setFeatures(QDockWidget.DockWidgetMovable |
                              QDockWidget.DockWidgetFloatable)
        
        
        self.InfoWidget.setWidget(self.InfoDialog)# Add the dock to the main window
        self.addDockWidget(Qt.LeftDockWidgetArea, self.InfoWidget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.DataWidget)
        self.tabifyDockWidget(self.DataWidget, self.InfoWidget,)
        # self.tabifyDockWidget(self.QuantifitWidget, self.SimWidget)
        # self.tabifyDockWidget(self.QuantifitWidget, self.InfoWidget)

        
        #============= Definition of Right QDialog  =================
        # 
        #        Definition of the Dock Widget:         
        #   that works as a container for the dialog widget

        self.SelectWidget = QDockWidget("Select", self)
        # Add the dock to the main window
        self.addDockWidget(Qt.RightDockWidgetArea, self.SelectWidget)
        
        #================== File menubar and toolbar ==================        
        # Exit the aplication

        # exit option for the menu bar File menu
        self.exit = QAction('Exit', self)
        self.exit.setShortcut('Ctrl+Q')
        # message for the status bar if mouse is over Exit
        self.exit.setStatusTip('Exit program')
        self.exit.triggered.connect(self.accept)

        
        #File
        openFile = QAction('Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open File')
        #self.connect(openFile, SIGNAL('triggered()'), self.open_file)
        openFile.triggered.connect(self.open_file)

        # Save File
        saveFile = QAction('Save', self)
        saveFile.setShortcut('Ctrl+S')
        saveFile.setStatusTip('Save File')
        saveFile.triggered.connect(self.save_file)

        self.vLegend = QAction('Legend', self)
        self.vLegend.setShortcut('Ctrl+L')
        self.vLegend.setStatusTip('Switches Legend Display off and on')
        self.vLegend.setCheckable (True)
        self.vLegend.setChecked(True)
        self.vLegend.triggered.connect(self.switchLegend)

        #-------------------- MenuBar --------------------
        # add actions to the menu bar
        menubar = self.menuBar()
        File = menubar.addMenu('&File')                
        
        File.addAction(openFile)
        File.addAction(saveFile)
        File.addAction(self.exit)


        view = self.menuBar().addMenu("&View")
        
        view.addSeparator()
        view.addAction(self.vLegend)
        
        self.vImage = []
        self.MviewImage = ['-','black', 'color', 'inverted','Si Window', 'Cursor','Crosshair']
        i = 0
        for key in self.MviewImage:
            if key == '-':
                view.addSeparator()
            else:
                self.vImage.append( QAction(key, self))
                #self.vLegend.setShortcut('Ctrl+L')
                #self.vLegend.setStatusTip('Switches Legend Display off and on')
                self.vImage[i].setCheckable (True)
                self.vImage[i].setChecked(False)
                if key == 'black':
                    self.vImage[i].setShortcut('Alt+b')
                if key == 'color':
                    self.vImage[i].setShortcut('Alt+c')
                if key == 'inverted':
                    self.vImage[i].setShortcut('Alt+i')
                if key == 'Cursor':
                    self.vImage[i].setShortcut('Alt+K')
                if key == 'Crosshair':
                    self.vImage[i].setShortcut('Alt+H')
                self.vImage[i].uniqueId =i+111
                self.vImage[i].triggered.connect(self.doImageView)

                view.addAction(self.vImage[i])
                i += 1
        
        self.help_menu = self.menuBar().addMenu("&Help")
        
        about_action = self.create_action("&About", 
            shortcut='F1', slot=self.on_about, 
            tip='About Quantifit')
        
        self.add_actions(self.help_menu, (about_action,))
        
    def switchLegend(self):
        if self.vLegend.isChecked():
            self.legend.show()        
        else:
            self.legend.hide()
            
    def onTabClose(self,index):
        if index>2:
            self.tab.removeTab(index)
        else:
            self.tab.hideTab(index)

    def updateTab(self,num):
        self.tabCurrent = num
        print('tab' ,num)
        if num <2:
            pass
            #self.SelectDialog.update()
        if num > 2:
            self.tags['images']['current'] = num -3
            SiTab = -1
            if 'SI' in self.tags['QF']:
                if 'SIimageTab' in self.tags['QF']['SI']:
                    SiTab = self.tags['QF']['SI']['SIimageTab']
                    print('SiTab', SiTab)
            if self.tags['images']['current'] != SiTab:
                
                self.ImageDialog.update()
                self.ProbeDialog.update()
            
    def viewButtonClicked(self,num):
        if num == 1:
            self.tags['QF']['GaussView'] = 1
        else:
            self.tags['QF']['GaussView'] = 0
        self.SelectDialog.update()

    def accept(self):       
        self.close()

    def doImageView(self):
        edit = self.sender()
        uid = edit.uniqueId-110
        key = self.MviewImage[uid]
        debug = 1
        if debug >0 :
            print('here key' , uid, key)
            
        if self.tabCurrent <3:
            if key == 'Cursor':
                if self.vImage[uid-1].isChecked() == True:
                    self.tags['QF']['Cursor'] = 1
                else:
                    self.tags['QF']['Cursor'] = 0
                    self.status.showMessage(" ")
                self.SelectDialog.update()
            
            if key == 'Crosshair':
                if self.vImage[uid-1].isChecked() == True:
                    self.tags['QF']['Crosshair'] = 1
                else:
                    self.tags['QF']['Crosshair'] = 0
                    self.status.showMessage(" ")
                self.SelectDialog.update()
            return
            #['cmap'] = 'gray'
            self.image[whichImage].plotImage()
            self.vImage[uid].setChecked(False)
            self.vImage[uid+1].setChecked(False)
        elif key == 'inverted':
            self.image[whichImage].dict['cmap'] = 'gray_r'
            self.image[whichImage].plotImage()
            self.vImage[uid].setChecked(False)
            self.vImage[uid-2].setChecked(False)
        elif key == 'color':
            self.image[whichImage].dict['cmap'] = 'jet'#hot
            self.image[whichImage].plotImage()
            self.vImage[uid-3].setChecked(False)
            self.vImage[uid-2].setChecked(False)
       
    def on_about(self):
        msg = "Quantifit version "+str(self.version)+"qt \n Copyright (c) Gerd Duscher 2025"
        QMessageBox.about(self, "About Quantifit", msg)

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)
    def create_action(  self, text, slot=None, shortcut=None, 
                        icon=None, tip=None, checkable=False, 
                        signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            action.triggered.connect(slot)

        if checkable:
            action.setCheckable(True)
        return action


    def keyPressEvent(self, event):
        
        key = event.key()
        #if self.SIDialog.visibleRegion().isEmpty():
        #    return
        #else:
        #    self.SIDialog.setFocus()
        if key == 16777234:
            si['Xpos']-=1
            if si['Xpos']<0:
                si['Xpos']=0
            else:
                print('left')
                self.SIDialog.setSlider()
        if key == 16777236:
            si['Xpos']+=1
            if si['Xpos']> si['Xsize']-1:
                si['Xpos']=si['Xsize']-1
            else:
                print('right')
                self.SIDialog.setSlider()
        if key == 16777235:
            si['Ypos']-=1
            if si['Ypos']<0:
                si['Ypos']=0
            else:
                print('up')
                
        if key == 16777237:
            si['Ypos']+=1
            if si['Ypos']> si['Ysize']-1:
                si['Ypos']=si['Ysize']-1
            else:
                print('down')
                
        if key == 16777232:
            si['Xpos']= 0
            si['Ypos']= 0
            print('home')
            self.SIDialog.setSlider()
        if key == 16777233:
            si['Xpos']= si['Xsize']-1
            si['Ypos']= si['Ysize']-1
            print('end')
            
        """
        self.SIDialog.slider1.setValue(si['Xpos'])
        self.SIDialog.slider2.setValue(si['Ypos'])
        self.SIDialog.setSlider()
        """
        
        
    def open_file(self, filename=None):

        key = pyTEMlib.file_tools.add_dataset_from_file(self.datasets, None, 'Channel')
        self.status.showMessage("opened" + list(self.datasets.keys())[0])
        self.main = list(self.datasets.keys())[0]
        self.dataset = self.datasets[self.main]
        if '_relationship' not in self.datasets:
            self.datasets['_relationship'] = {}
        for key in self.datasets.keys():
            if isinstance(self.datasets[key], sidpy.Dataset):
                if 'SPECT' in self.datasets[key].data_type.name:
                    self.status.showMessage("opened spectrum " + list(self.datasets.keys())[0])
                    
                    if len(self.DataDialog.spectrum_list.findItems('None', Qt.MatchExactly))>0:
                        self.DataDialog.spectrum_list.clear()
                    if len(self.DataDialog.spectrum_list.findItems(key, Qt.MatchStartsWith))==0:
                        self.DataDialog.spectrum_list.addItems([f'{key}: {self.datasets[key].title}'])
                           
                elif 'IMAGE' in self.datasets[key].data_type.name:
                    if 'survey' in self.datasets[key].title.lower():
                        if len(self.DataDialog.survey_list.findItems('None', Qt.MatchExactly))>0:
                            self.DataDialog.survey_list.clear()  
                        if len(self.DataDialog.survey_list.findItems(key, Qt.MatchStartsWith))==0:
                            self.DataDialog.survey_list.addItem(f'{key}: {self.datasets[key].title}')
                    else:
                        if len(self.DataDialog.image_list.findItems('None', Qt.MatchExactly))>0:
                            self.DataDialog.image_list.clear()  
                        if len(self.DataDialog.image_list.findItems(key, Qt.MatchStartsWith))==0:
                            self.DataDialog.image_list.addItem(f'{key}: {self.datasets[key].title}')
           

                """
                self.tags['images'][str(imInd)].plotImage()
                winds = self.tabifiedDockWidgets ( self.InfoWidget )
                self.ImageWidget.setVisible(True)
                self.ProbeWidget.setVisible(True)
                self.ImageWidget.raise_()

                self.ImageDialog.update()
                self.ProbeDialog.update()
                """

            else:
                if '_' != key[0]:
                    print('Did not recognize file type: ', f'{key}')
        
        self.InfoDialog.updateInfo()   
        #ft.plot_tags(qf, 'new')   
        self.setWindowTitle('Quantifit version '+str(1) +'qt serial #: 1 - ')# +tags['filename'])
                
    def save_file(self, filename=None):
        pass

    def set_cursor_values(self):
        values = self.cursor.getRegion()
        self.left_cursor_value.setText(f'{values[0]:.3f}')
        self.right_cursor_value.setText(f'{values[1]:.3f}')

    def plotUpdate(self,key = 'All'):
        
        if self.main in self.datasets:
            if self.datasets[self.main].data_type.name == 'SPECTRUM':
                plt = self.plotParamWindow
                if self.cursor is None:
                    cursor_values = None
                else:
                    cursor_values = self.cursor.getRegion()
                    
                plt.clear()
                ene = np.array(self.datasets[self.main].get_spectral_dims(return_axis=True)[0])
                energy_scale = np.append(ene, ene[-1])
                curve = pg.PlotCurveItem(np.array(energy_scale), np.array(self.datasets[self.main])*self.intensity_scale, 
                                         stepMode=True, fillLevel=0,
                                         pen = 'blue',  brush=(0,0,255,30), fillBrush=(0,0,255,30),
                                         name=self.datasets[self.main].title) 
                curve.setPen(pg.mkPen('blue', width=2))
                                                      
                plt.addItem(curve)
                plt.addLine(y=0, pen='gray')
                plt.setWindowTitle(f'Quantifit {self.version}')
                if self.intensity_scale == 1.0:
                    plt.setLabel('left', 'intensity', units='counts')
                else:
                    plt.setLabel('left', 'scattering probability', units='ppm')
                plt.setLabel('bottom', 'energy_loss', units='eV')

                print((np.array(self.datasets[self.main])*self.intensity_scale).min())
                self.legend = plt.addLegend()
                if cursor_values == None:
                    cursor_values = (energy_scale[10], energy_scale[90])
                self.cursor = pg.LinearRegionItem(values=cursor_values,
                                                  orientation='vertical')
                self.cursor.sigRegionChangeFinished.connect(self.set_cursor_values)
                plt.addItem(self.cursor)
        
                colors = (  'red','green', 'orange', 'purple', 'cyan', 'magenta', 'grey', 'lightgrey', 'black','black')
        
                for i, key in enumerate(self.add_spectrum):
                    ene = np.array(self.datasets[key].get_spectral_dims(return_axis=True)[0])
                    energy_scale = np.append(ene, ene[-1])
                    curve = pg.PlotCurveItem(np.array(energy_scale), np.array(self.datasets[key])*self.intensity_scale, 
                                             pen = colors[i], stepMode=True, 
                                             padding = 0, name=self.datasets[key].title) #, name=memtags['name'])
                    plt.addItem(curve)
                self.tab.setCurrentWidget(self.plot1)
                    
            elif self.datasets[self.main].data_type.name == 'IMAGE':
                
        
        
                self.plotParamWindow3.setImage(np.array(self.datasets[self.main]))
                self.img = self.plotParamWindow3.getImageItem()
                self.view = self.plotParamWindow3.getView()
                self.histo = self.plotParamWindow3.ui.histogram
                self.view.setAspectLocked(lock=True, ratio=1)
                x =self.datasets[self.main].x
                y =self.datasets[self.main].y
                
                tr = QTransform()  # prepare ImageItem transformation:
                tr.scale(x[1]-x[0], y[1]-y[0])       # scale horizontal and vertical axes
                # tr.translate(-1.5, -1.5) # move 3x3 image to locate center at axis origin

        
                self.img.setTransform(tr) 
                #self.img.setRect(x[0], y[0], x[-1]-x[0], y[-1]-y[0])
                self.roi = self.plotParamWindow3.getRoiPlot()
                self.plotParamWindow3.roi.setSize((1.000000, 1.000000))
        
                scale = pg.ScaleBar(size=10, pen = 'w', suffix = 'nm')
                scale.setParentItem(self.view)
                scale.anchor((1, 1), (1, 1), offset=(-20, -20))
                
                #print ('\n ii:', self.plotParamWindow4.parentBounds())
                self.plotParamWindow3.autoRange()
        
                #imagetab = self.parent.tab.addTab(plot4, 'Image')
                #self.parent.tab.setTabsClosable(True)

                self.tab.setCurrentWidget(self.plot3)
        

                #self.parent.tab.currentChanged[int].connect(self.parent.updateTab)
        
        
def main(args=[]):
    app=QApplication(args)
    f=MainWidget()        
    f.show()
    app.exec()


if __name__ == "__main__":
    #import sys
    main()#sys.argv)
    
