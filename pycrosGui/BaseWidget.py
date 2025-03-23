
# ################################################################
# 1######## pycrosGui BaseWidget
# # part of the pycroscopy ecosystem
# #
# # by Gerd Duscher
# # Start Feb 2025
# This Base Widget is to be extended for pycroscopy GUIs
# running under python 3 using pyqt, and pyQT5 as GUI mashine
# ################################################################
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

import os as os
import numpy as np

import pyqtgraph as pg
import sys
sys.path.insert(0, '../pyTEMlib/')


# =============================================================
#   Include pycroscopy Libraries                                      #
# =============================================================
import pyTEMlib
print('pyTEMlib version :', pyTEMlib.__version__)
import pyTEMlib.file_tools
import sidpy

from .DataDialog import DataDialog
from .periodic_table import PeriodicTable

class ImageView(pg.ImageView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui.roiBtn.setChecked(False)
        # self.roiClicked()
        
    def roiChanged(self):
        super().roiChanged()
        for i in range(len(self.roiCurves)):
            self.roiCurves[i].setPen('black')
        
    
class BaseWidget(QtWidgets.QMainWindow):    
    def __init__(self, sidebar=[], filename=None):
        super().__init__()
        self.version = '2025-1-1'
        self.dataset = None
        self.datasets = {}

        self.extensions = '*'
        self.filename = filename
        self.dataset_list = ['None']
        self.image_list = ['Sum']
        if filename is None:
            self.dir_name = pyTEMlib.file_tools.get_last_path()
            self.filename = ''
        else:
            self.dir_name = os.path.dirname(filename)
            self.filename = filename
        if not os.path.isdir(self.dir_name):
            self.dir_name = '.'
        self.save_path = True

        self.image = 'Sum'
        self.main = ""
        self.cursor = None
        self.intensity_scale = 1.0

        self.x = 0 
        self.y = 0
        self.bin_x = 1
        self.bin_y = 1
        
        self.start_channel = -1
        self.end_channel = -2
        
        self.path = '.'
        self.setWindowTitle('pycrosGUI version '+str(self.version) +'qt serial #: 1')
        
        self.add_spectrum = []
        self.add_si_spectrum = []
        self.statusBar()
        self.tabCurrent = 1
        # ============================================================================
        # =============== Definition of the Main Window LayOut =======================
        # ============================================================================
        # Widget that contains the Plot and toolbar
        centralWidget = QtWidgets.QWidget()
        self.centralWidget = centralWidget
        
        #============= Definition of Figure and Dialog Windows  for Parameters =================
        
        self.height = 450
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        self.height = screen.height() 
        self.width = screen.width() 
        self.periodic_table = PeriodicTable(self)
	        
        ## Switch to using white background and black foreground
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        # Creating an instance of the Figure
        self.plotParamWindow  = pg.PlotWidget()
        self.plotParamWindow2 = pg.PlotWidget()
        self.plotParamWindow3 = pg.PlotWidget()
        
        
        self.plotParamWindow.plot((0,1),(0,1))
        
        plotLayout  = QtWidgets.QVBoxLayout()
        plotLayout1 = QtWidgets.QVBoxLayout()
        plotLayout3 = QtWidgets.QVBoxLayout()

        validfloat = QtGui.QDoubleValidator()
        top_layout = QtWidgets.QHBoxLayout()
        self.left_cursor_label = QtWidgets.QLabel("Cursor Start")
        self.left_cursor_value = QtWidgets.QLineEdit(" 100.0")
        self.left_cursor_value.setValidator(validfloat)
        top_layout.addWidget(self.left_cursor_label)
        top_layout.addWidget(self.left_cursor_value)
        self.right_cursor_label = QtWidgets.QLabel("End")
        self.right_cursor_value = QtWidgets.QLineEdit(" 100.0")
        self.right_cursor_value.setValidator(validfloat)
        top_layout.addWidget(self.right_cursor_label)
        top_layout.addWidget(self.right_cursor_value)
        
        top_widget = QtWidgets.QWidget()
        top_widget.setLayout(top_layout)
        self.plot1 = QtWidgets.QWidget()

        plotLayout1.addWidget(top_widget)        
        plotLayout1.addWidget(self.plotParamWindow)        
        self.plot1.setLayout(plotLayout1)

        self.plot2 = QtWidgets.QWidget()
        self.si_layout = QtWidgets.QGridLayout()
        self.plot2.setLayout(self.si_layout)
        self.si_layout.setSpacing(0)

        self.si_image_data = np.zeros((2,2))
        self.si_view= pg.GraphicsView()
        self.si_img_view = pg.ViewBox()
        self.si_img_view.setAspectLocked()
        self.si_view.setCentralItem(self.si_img_view)
        self.si_layout.addWidget(self.si_view, 0, 0)

        self.si_plot= pg.PlotWidget()
        self.si_layout.addWidget(self.si_plot, 0, 1)

        self.si_image = pg.ImageItem(self.si_image_data)
        
        self.si_img_view.addItem(self.si_image)
        self.si_img_view.scene().sigMouseClicked.connect(self.mouse_clicked)
        
        self.si_roi = pg.RectROI([0, 0], [1, 1], pen=(0, 9))
        self.si_roi.sigRegionChanged.connect(self.update_roi)
        self.si_img_view.addItem(self.si_roi)
        self.si_roi.setZValue(10)

        self.plot3 = QtWidgets.QWidget()

        self.titleLabel =  QtWidgets.QLabel(" ") # pg.TextItem('', color='gray') ## , size='11pt', parent=self.plot3_view)
        
        self.image_item = ImageView()
        self.img = self.image_item.getImageItem()    
        self.img.hoverEvent = self.imageHoverEvent
        self.img.mouseClickEvent = self.mouse_clicked_image

        view = self.image_item.getView()
        pos = np.array([[0,0]])
        self.blobs = pg.ScatterPlotItem(pos=pos, pen=None , symbol='o', size=10, brush=pg.mkBrush(200,0,0,50), name='atoms')
        self.blobs.setZValue(100)
        self.blobs.setVisible(False)
        view.addItem(self.blobs)

        self.select_roi = pg.CircleROI(pos=[-.1, -.1], radius=0.1, pen=(0,9), parent=self.img)
        self.select_roi.isVisible = False
        
        plotLayout3.addWidget(self.titleLabel) 
        plotLayout3.addWidget(self.image_item)        
        self.plot3.setLayout(plotLayout3)
        
        self.tab = QtWidgets.QTabWidget()
        self.tab.addTab(self.plot1, 'Spectrum')
        self.tab.addTab(self.plot2, 'Spectral Image')
        self.tab.addTab(self.plot3, 'Image')
        self.tab.currentChanged[int].connect(self.updateTab)
        self.tab.setTabsClosable(True)
        self.tab.tabCloseRequested.connect(self.onTabClose)
        
        #self.tab.setTabIcon (0, QIcon(Empty))        
        plotLayout.addWidget(self.tab)
        
        self.status =  self.statusBar() #QStatusBar()
        self.status.showMessage(" No data")
        
        # Adding the layout to the widget 
        centralWidget.setLayout(plotLayout)
        # Making that Widget the central widget for the window
        self.setCentralWidget(centralWidget)
        #self.tabifiedDockWidgets(centralWidget)
        
        #============= Definition Left QDialog  =================
        # 
        #        Definition of the Dock Widget:         
        #  that works as a container for the dialog widget
        
        self.DataWidget = QtWidgets.QDockWidget("Datasets ", self)
        self.DataDialog = DataDialog(self)
        self.DataWidget.setWidget(self.DataDialog)# Add the dock to the main window
        self.DataWidget.visibilityChanged.connect(self.update_DataDialog)
        
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.DataWidget)
        
        #============= Definition of Right QDialog  =================
        # 
        #        Definition of the Dock Widget:         
        #   that works as a container for the dialog widget

        self.SelectWidget = QtWidgets.QDockWidget("Select", self)
        # Add the dock to the main window
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.SelectWidget)
        
        #================== File menubar and toolbar ==================        
        # Exit the aplication

        # exit option for the menu bar File menu
        self.exit = QtWidgets.QAction('Exit', self)
        self.exit.setShortcut('Ctrl+Q')
        # message for the status bar if mouse is over Exit
        self.exit.setStatusTip('Exit program')
        # newer connect style (PySide/PyQT 4.5 and higher)
        self.exit.triggered.connect(self.accept)

        
        #File
        openFile = QtWidgets.QAction('Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open File')
        openFile.triggered.connect(self.open_file)

        # Save File
        saveFile = QtWidgets.QAction('Save', self)
        saveFile.setShortcut('Ctrl+S')
        saveFile.setStatusTip('Save File')
        saveFile.triggered.connect(self.save_file)

        # Show Metadata
        showMetadata = QtWidgets.QAction('Metadata', self)
        showMetadata.setShortcut('Ctrl+M')
        showMetadata.setStatusTip('Show Metadata')
        showMetadata.triggered.connect(self.show_metadata)
        
        # Show Metadata
        originalMetadata = QtWidgets.QAction('Original Meta', self)
        originalMetadata.setStatusTip('Show Original Metadata')
        originalMetadata.triggered.connect(self.show_metadata_original)

        # Show Metadata
        provenance = QtWidgets.QAction('Provenance', self)
        provenance.setStatusTip('Show provenance of current dataset')
        provenance.triggered.connect(self.show_provenance)

        self.vLegend = QtWidgets.QAction('Legend', self)
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
        
        File.addAction(showMetadata)
        File.addAction(originalMetadata)
        File.addAction(provenance)
        File.addAction(self.exit)

        view = self.menuBar().addMenu("&View")
        
        view.addSeparator()
        view.addAction(self.vLegend)
        
        self.vImage = []
        self.MviewImage = ['Cursor', '-','black', 'color', 'inverted','Si Window', 'Crosshair']
        i = 0
        for key in self.MviewImage:
            if key == '-':
                view.addSeparator()
            else:
                self.vImage.append( QtWidgets.QAction(key, self))
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
                    self.vImage[i].setChecked(True)
                if key == 'Crosshair':
                    self.vImage[i].setShortcut('Alt+H')
                self.vImage[i].uniqueId =i+111
                
                view.addAction(self.vImage[i])
                i += 1
        
        self.help_menu = self.menuBar().addMenu("&Help")
        
        about_action = self.create_action("&About", 
            shortcut='F1', slot=self.on_about, 
            tip='About pycrosGUI')
        
        self.add_actions(self.help_menu, (about_action,))
    
    def add_sidebar(self, dialog):
        dialogWidget = QtWidgets.QDockWidget(dialog.name, self)
        
        dialogWidget.setFeatures(QtWidgets.QDockWidget.DockWidgetMovable |
                                 QtWidgets.QDockWidget.DockWidgetFloatable)
        dialogWidget.setWidget(dialog)# Add the dock to the main window
        self.addDockWidget (QtCore.Qt.LeftDockWidgetArea, dialogWidget)
        
        return dialogWidget
        
    def imageHoverEvent(self, event):
        """Show the position, pixel, and value under the mouse cursor.
        """
        if event.isExit():
            self.setTitle("")
            return
        pos = event.pos()
        data = self.img.image
        i, j = pos.x(), pos.y()
        i = int(np.clip(i, 0, data.shape[0] - 1))
        j = int(np.clip(j, 0, data.shape[1] - 1))
        val = data[i, j]
        ppos = self.img.mapToParent(pos)
        x = ppos.x()
        units = self.dataset.x.units
        self.setTitle(f"pos: ({x:0.1f}, {x:0.1f}){units} - pixel: ({i:d}, {j:d})  value: {val:3g}")
    
    def mouse_clicked_image(self, mouseClickEvent):
        print('BaseWidget mouse_clicked_image', mouseClickEvent.pos)
        
        self.x_pixel = int(np.clip(pos.x(), 0, self.img.image.shape[0] - 1))
        self.y_pixel = int(np.clip(pos.y(), 0, self.img.image.shape[1] - 1))
            
    def setTitle(self, title=None, **args):
        """
        Set the title of the plot. Basic HTML formatting is allowed.
        If title is None, then the title will be hidden.
        """
        if title is None:
            self.titleLabel.setVisible(False)
        else:
            self.titleLabel.setVisible(True)
            self.titleLabel.setText(title, **args)

    def show_metadata_original(self):
        self.show_dictionary(self.dataset.original_metadata,
                             name= 'Original Metadata - ')

    def show_metadata(self):
        self.show_dictionary(self.dataset.metadata, 
                             name='Metadata')
    
    def show_provenance(self):
        self.show_dictionary(self.dataset.provenance, 
                             name='Provenance' )

    def show_dictionary(self, metadata, name=''):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle(name + " - " + self.dataset.title)
        dialog.resize(400, 300)

        tree = QtWidgets.QTreeWidget(dialog)
        tree.setHeaderLabels(["Key", "Value"])
        tree.setColumnWidth(0, 150)
        tree.setGeometry(10, 10, 380, 280)

        def populate_tree(parent, data):
            for key, value in data.items():
                if isinstance(value, dict):
                    item = QtWidgets.QTreeWidgetItem([key])
                    parent.addChild(item)
                    populate_tree(item, value)
                else:
                    item = QtWidgets.QTreeWidgetItem([key, str(value)])
                    parent.addChild(item)

        root = QtWidgets.QTreeWidgetItem(["Metadata - "])
        tree.addTopLevelItem(root)
        populate_tree(root, metadata)
        tree.expandAll()

        dialog.exec_()

    def mouse_clicked(self, mouseClickEvent):
        if self.tabCurrent != 1:
            return
        point = self.si_img_view.mapSceneToView(mouseClickEvent.scenePos())
        x = point.x()
        y = point.y()
        if x>-0.5 and x+0.5<self.si_image_data.shape[0]:
            x = int(x+0.5)    
        else: 
            return
        if y>-0.5 and y+0.5<self.si_image_data.shape[1]:
            y = int(y+0.5)
        else: 
            return
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ShiftModifier:
            self.add_si_spectrum.append([x, y])
        elif modifiers == QtCore.Qt.ControlModifier:
            self.add_si_spectrum = []
            self.x = x
            self.y = y
        else:
            self.x = x
            self.y = y
        self.plotUpdate()
         
    def add_image_dataset(self, key, name, dataset, data_type='IMAGE'):
        self.datasets[key] = dataset
        self.datasets['_relationship'][key] = key
        self.datasets[key].data_type = data_type
        self.datasets[key].title = name
        self.datasets['_relationship']['image'] = key
        self.update_sidebar()

    def update_sidebar(self):
        for dock_widget in self.findChildren(QtWidgets.QDockWidget):
            if hasattr(dock_widget.widget(), 'update_sidebar'):
                if dock_widget.isVisible():
                    dock_widget.widget().update_sidebar()

    def update_roi(self,roi):
        pass

    def onTabClose(self,index):
        if index>2:
            self.tab.removeTab(index)
        else:
            self.tab.hideTab(index)
    
    def updateTab(self,num):
        self.tabCurrent = num
        # print('tab' ,num)
        
    def accept(self):       
        self.close()
    
    def switchLegend(self):
        if self.vLegend.isChecked():
            self.show = True
        else:
            self.show = False
        
    def on_about(self):
        msg = f"pycrosGUI version {self.version}qt \n part of the pycrosocpy ecosystem\n by Gerd Duscher 2025 "
        QtGui.QMessageBox.about(self, "About pycrosGUI", msg)

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)
    
    def create_action(  self, text, slot=None, shortcut=None, 
                        icon=None, tip=None, checkable=False, 
                        signal="triggered()"):
        action = QtWidgets.QAction(text, self)
        if icon is not None:
            action.setIcon(QtWidgets.QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            #self.connect(action, SIGNAL(signal), slot)
            action.triggered.connect(slot)

        if checkable:
            action.setCheckable(True)
        return action

    def keyPressEvent(self, event):
        key = event.key()
        if not isinstance(self.dataset, sidpy.Dataset):
            return
        if 'SPECTRAL' in self.dataset.data_type.name:
            if key == 16777234:
                self.x-=1
                if self.x<0:
                    self.x=0
            elif key == 16777236:
                self.x+=1
                if self.x > self.dataset.shape[0]-1:
                    self.x = self.dataset.shape[0]-1
            elif key == 16777237:
                self.y -= 1
                if self.y < 0:
                    self.y = 0
            elif key == 16777235:
                self.y += 1
                if self.y > self.dataset.shape[1]-1:
                    self.y = self.dataset.shape[1]-1
            elif key == 16777232:
                self.x = 0
                self.y = 0
            self.plotUpdate()

    def get_additional_metadata(self):
        print('get additional metadata')
        
    def open_file(self, filename=None):

        self.main = pyTEMlib.file_tools.add_dataset_from_file(self.datasets, None, 'Channel', single_dataset=False)
        print(self.main)
        
        #if self.filename[-3:] == 'emd':
        #    self.get_additional_metadata()
        self.status.showMessage("opened" + list(self.datasets.keys())[0])
        self.main = list(self.datasets.keys())[0]
        self.set_dataset()
        if '_relationship' not in self.datasets:
            self.datasets['_relationship'] = {}
        self.update_DataDialog()
            
    def update_DataDialog(self):
        for key in self.datasets.keys():
            if isinstance(self.datasets[key], sidpy.Dataset):
                if 'SPECT' in self.datasets[key].data_type.name:
                    self.status.showMessage("opened spectrum " + list(self.datasets.keys())[0])
                    
                    if len(self.DataDialog.spectrum_list.findItems('None', QtCore.Qt.MatchExactly))>0:
                        self.DataDialog.spectrum_list.clear()
                    if len(self.DataDialog.spectrum_list.findItems(key, QtCore.Qt.MatchStartsWith))==0:
                        self.DataDialog.spectrum_list.addItems([f'{key}: {self.datasets[key].title}'])
                elif 'IMAGE_STACK' == self.datasets[key].data_type.name: 
                    self.status.showMessage("opened image stack " + list(self.datasets.keys())[0])
                    if len(self.DataDialog.image_list.findItems('None', QtCore.Qt.MatchExactly))>0:
                        self.DataDialog.image_list.clear()  
                    if len(self.DataDialog.image_list.findItems(key, QtCore.Qt.MatchStartsWith))==0:
                        self.DataDialog.image_list.addItem(f'{key}: {self.datasets[key].title}')
                elif 'IMAGE' in self.datasets[key].data_type.name:
                    if 'survey' in self.datasets[key].title.lower():
                        if len(self.DataDialog.survey_list.findItems('None', QtCore.Qt.MatchExactly))>0:
                            self.DataDialog.survey_list.clear()  
                        if len(self.DataDialog.survey_list.findItems(key, QtCore.Qt.MatchStartsWith))==0:
                            self.DataDialog.survey_list.addItem(f'{key}: {self.datasets[key].title}')
                    else:
                        if len(self.DataDialog.image_list.findItems('None', QtCore.Qt.MatchExactly))>0:
                            self.DataDialog.image_list.clear()  
                        if len(self.DataDialog.image_list.findItems(key, QtCore.Qt.MatchStartsWith))==0:
                            self.DataDialog.image_list.addItem(f'{key}: {self.datasets[key].title}')
            else:
                if '_' != key[0]:
                    print('Did not recognize file type: ', f'{key}')
        self.setWindowTitle('PyCrosGUI version '+str(1) +' serial #: 1 - ')# +tags['filename'])
        
    def save_file(self, filename=None):
        file_name = self.datasets[self.main].title+'.hf5'
        h5_group = pyTEMlib.file_tools.save_dataset(self.datasets, file_name, qt=True)
        h5_group.file.close()   
        self.status.showMessage(' File saved')
         
    def set_dataset(self):
        if isinstance(self.dataset, sidpy.Dataset):
            if 'plot' not in self.dataset.metadata:
                self.dataset.metadata['plot'] = {}
            if 'SPECTRAL' in self.dataset.data_type.name:
                self.dataset.metadata['plot']['x'] = self.x
                self.dataset.metadata['plot']['y'] = self.y
            if 'SPECTRUM' in self.dataset.data_type.name:
                self.dataset.metadata['plot']['x'] = 0
                self.dataset.metadata['plot']['y'] = 0
            if 'experiment' not in self.dataset.metadata:
                self.dataset.metadata['experiment'] = {}
        if self.main in self.datasets:
            self.dataset = self.datasets[self.main]
            self.status.showMessage("switched to " + list(self.datasets.keys())[0])
            if 'plot' not in self.dataset.metadata:
                self.dataset.metadata['plot'] = {}
            if 'x' in self.dataset.metadata['plot']:
                self.x = self.dataset.metadata['plot']['x']
                self.y = self.dataset.metadata['plot']['y']
            else:
                self.x = 0
                self.y = 0
        
    def plotUpdate(self,key = 'All'):
        self.plot_features = {} 
        self.dataset = self.datasets[self.main]
        if not isinstance(self.dataset, sidpy.Dataset):
            return
       
        if 'SPECT' in self.dataset.data_type.name:
            if 'SPECTRAL' in self.datasets[self.main].data_type.name:
                self.si_image_data = np.array(self.datasets[self.main]).sum(axis=2) 
                self.si_image.setImage(self.si_image_data)
                plt= self.si_plot
                self.si_roi.setPos(self.x,self.y)
            else:
                plt = self.plotParamWindow
                if self.cursor is None:
                    cursor_values = None
                else:
                    cursor_values = self.cursor.getRegion()
            plt.clear()
            spectrum, label =self.get_spectrum(self.main)
            ene = np.array(self.dataset.get_spectral_dims(return_axis=True)[0])
            energy_scale = np.append(ene, ene[-1])
            curve = pg.PlotCurveItem(np.array(energy_scale), spectrum, 
                                        stepMode=True, fillLevel=0,
                                        pen = 'blue',  brush=(0,0,255,30), fillBrush=(0,0,255,30),
                                        name=label) 
            curve.setPen(pg.mkPen('blue', width=2))
                                                    
            plt.addItem(curve)
            plt.addLine(y=0, pen='gray')
            plt.setWindowTitle(f'PycrosGUI {self.version}')
            if self.intensity_scale == 1.0:
                plt.setLabel('left', 'intensity', units='counts')
            else:
                plt.setLabel('left', 'scattering probability', units='ppm')
            plt.setLabel('bottom', 'energy_loss', units='eV')

            plt.addLegend()
            
            colors = ('red', 'green', 'orange', 'purple', 'cyan', 'magenta', 'grey', 'lightgrey', 'black','black')
            for i, pos in enumerate(self.add_si_spectrum):
                spectrum, label = self.get_spectrum(pos)
                curve = pg.PlotCurveItem(np.array(energy_scale), spectrum, 
                                            pen = colors[i%10], stepMode=True, 
                                            padding = 0, name=label) #, name=memtags['name'])
                plt.addItem(curve)

            self.plot_additional_features(plt)

            if 'SPECTRAL' in self.datasets[self.main].data_type.name:
                self.tab.setCurrentWidget(self.plot2)
            else:
                if cursor_values == None:
                    cursor_values = (energy_scale[10], energy_scale[90])
                self.cursor = pg.LinearRegionItem(values=cursor_values,
                                                orientation='vertical')
                self.cursor.sigRegionChangeFinished.connect(self.set_cursor_values)
                plt.addItem(self.cursor)
                self.tab.setCurrentWidget(self.plot1)
        elif 'IMAGE' in self.datasets[self.main].data_type.name:
            
            if 'IMAGE_STACK' in self.datasets[self.main].data_type.name:
                dims = self.dataset.get_dimensions_by_type(sidpy.DimensionType.TEMPORAL, return_axis=True)
                if len(dims)>1:
                    print('old dm3 dataset')
                    data_set = sidpy.Dataset.from_array(np.swapaxes(np.array(self.dataset),2, 0), 'stack')
                    data_set.set_dimension(0, sidpy.Dimension(np.arange(data_set.shape[0]),
                                                              'z', units='frame', quantity='frame',
                                                              dimension_type='temporal'))
                    data_set.set_dimension(1, sidpy.Dimension(np.arange(data_set.shape[1]), 
                                                              name='x', units='nm', quantity='Length',
                                                              dimension_type='spatial'))
                    data_set.set_dimension(2, sidpy.Dimension(np.arange(data_set.shape[2]),
                                                              'y', units='nm', quantity='Length',
                                                              dimension_type='spatial'))
                    data_set.data_type = 'image_stack'
                    data_set.metadata['experiment'] = {'acceleration_voltage': 200000,
                                                       'convergence_angle': 30,
                                                       'collection_angle': 50}
                    data_set.title = self.dataset.title
                    self.dataset = data_set
                    dims = [data_set.z]
                self.image_item.setImage(np.array(self.dataset), xvals=dims[0].values)
            else:
                self.image_item.setImage(np.array(self.dataset))

            self.img = self.image_item.getImageItem()
            self.view = self.image_item.getView()
            self.histo = self.image_item.ui.histogram
            self.view.setAspectLocked(lock=True, ratio=1)
            dims = self.dataset.get_dimensions_by_type(sidpy.DimensionType.SPATIAL, return_axis=True)
            if len(dims) <1:
                dims  = self.dataset.get_dimensions_by_type(sidpy.DimensionType.RECIPROCAL, return_axis=True)
            if len(dims) <1:
                return
            x =dims[0]
            y =dims[1]
            
            tr = QtGui.QTransform()  # prepare ImageItem transformation:
            tr.scale(x[1]-x[0], y[1]-y[0])       # scale horizontal and vertical axes
            self.img.setTransform(tr) 
            self.img.setRect(x[0], y[0], x[-1]-x[0], y[-1]-y[0])
            # self.roi = self.plotParamWindow3.getRoiPlot()

            # self.plotParamWindow3.roi.setSize((2.000000, 2.000000))
    
            scale = pg.ScaleBar(size=10, pen = 'w', suffix = x.units)
            scale.setParentItem(self.view)
            scale.anchor((1, 1), (1, 1), offset=(-20, -20))
            
            self.plot_additional_features(self.view)
            self.view.setRange(xRange=[x[0], x[-1]], yRange=[y[0], y[-1]], padding=0)   
            
            """# self.plotParamWindow3.autoRange()
            
            print('new)')
            child_item = self.view.allChildItems()
            for item in child_item:
                print(item)
            print(self.view.allChildren())
            childs = self.view.allChildren()
            for child in childs:
                print(child)
            """
            self.tab.setCurrentWidget(self.plot3)
    
    def plot_additional_features(self, plt):
        """
        EMPTY: to be extended by the child classes
        """
        pass

    def get_spectrum(self, key=None):
        if key is None:
            key = self.main

        if isinstance(key, list):
            x = key[0]
            y = key[1]
            key = self.main
        else:
            x = self.x
            y = self.y

        if isinstance(self.datasets[key], sidpy.Dataset):
            if self.datasets[key].data_type == sidpy.DataType.SPECTRUM:
                spectrum = np.array(self.datasets[key])
                label = self.datasets[key].title
            else:
                image_dims = self.datasets[key].get_dimensions_by_type(sidpy.DimensionType.SPATIAL)
                selection = []
                bin_x = self.bin_x
                bin_y = self.bin_y
               
                for dim, axis in self.datasets[key]._axes.items():
                    # print(dim, axis.dimension_type)
                    if axis.dimension_type == sidpy.DimensionType.SPATIAL:
                        if dim == image_dims[0]:
                            selection.append(slice(x, x + bin_x))
                        else:
                            selection.append(slice(y, y + bin_y))

                    elif axis.dimension_type == sidpy.DimensionType.SPECTRAL:
                        selection.append(slice(None))
                    elif axis.dimension_type == sidpy.DimensionType.CHANNEL:
                        selection.append(slice(None))
                    else:
                        selection.append(slice(0, 1))
                
                spectrum = np.array(self.datasets[key][tuple(selection)].mean(axis=tuple(image_dims)))
                label = f" {self.datasets[key].title} {x}, {y}"
        else:
            spectrum = self.datasets[key] 
            label = key    
        spectrum *= self.intensity_scale
        return spectrum.squeeze(), label
    
    def get_spectrum_dataset(self, key=None):
        if self.dataset.data_type.name == 'SPECTRUM':
            return  self.dataset
        else:
            spectrum, label = self.get_spectrum(key) 
            spectrum = self.dataset[0, 0].like_data(spectrum)
            spectrum.data_type = 'spectrum'
            spectrum.title = label
            return spectrum  
        
    def set_cursor_values(self):
        values = self.cursor.getRegion()
        self.left_cursor_value.setText(f'{values[0]:.3f}')
        self.right_cursor_value.setText(f'{values[1]:.3f}')
