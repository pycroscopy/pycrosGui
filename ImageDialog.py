#####################################################################
#
# Part of pycrosGUI
# of pycroscopy ecosystem
#
# ImageDialog: SImage processing dialog.
#       
#       
####################################################################
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
import pyqtgraph as pg

import numpy as np
import sidpy
import scipy

from pyTEMlib import image_tools
import pyTEMlib.probe_tools
import pyTEMlib.atom_tools


class ImageDialog(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ImageDialog, self).__init__(parent)
    
        self.parent = parent
        self.set_energy = True
        layout = self.get_sidbar()
        self.setLayout(layout)    
        self.setWindowTitle("Image")

    def get_sidbar(self): 
        validfloat = QtGui.QDoubleValidator()
        validint = QtGui.QIntValidator()     
        
        layout = QtWidgets.QGridLayout()
        row = 0 
        self.mainList = QtWidgets.QComboBox(self)
        self.mainList.addItem("None")
        layout.addWidget(self.mainList,  row,0, 1, 3)
        layout.setColumnStretch(0, 3)  

        self.mainList.activated[str].connect(self.update_image_dataset)
        
        row += 1
        self.regButton = QtWidgets.QPushButton()
        self.regButton.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.regButton.setText("Registration")
        layout.addWidget(self.regButton,  row,0, 1, 3)
        layout.setColumnStretch(0, 3) 
        #self.scaleButton.clicked.connect(self.rigi_registration)
        
        row += 1
        self.rigid_regButton =  QtWidgets.QPushButton()
        self.rigid_regButton.setText("Rigid Reg.")
        self.rigid_regButton.setCheckable(True)
        layout.addWidget(self.rigid_regButton,  row, 0)
        self.rigid_regButton.clicked.connect(self.rigid_registration)
        
        self.demon_regButton =  QtWidgets.QPushButton()
        self.demon_regButton.setText("Demon Reg.")
        self.demon_regButton.setCheckable(True)
        layout.addWidget(self.demon_regButton,  row, 1)
        self.demon_regButton.clicked.connect(self.demon_registration)
        
        self.all_regButton =  QtWidgets.QPushButton()
        self.all_regButton.setText("Both Reg.")
        self.all_regButton.setCheckable(True)
        layout.addWidget(self.all_regButton,  row, 2)
        #self.all_regButton.clicked.connect(self.all_registration)
        
        row += 1
        self.sumButton =  QtWidgets.QPushButton()
        self.sumButton.setText("Sum")
        self.sumButton.setCheckable(True)
        layout.addWidget(self.sumButton,  row, 0)
        self.sumButton.clicked.connect(self.sum_stack)
        
        self.averageButton =  QtWidgets.QPushButton()
        self.averageButton.setText("Average")
        self.averageButton.setCheckable(True)
        layout.addWidget(self.averageButton,  row, 1)
        self.averageButton.clicked.connect(self.average_stack)
        
        self.driftButton =  QtWidgets.QPushButton()
        self.driftButton.setText("Get Drift")
        self.driftButton.setCheckable(True)
        layout.addWidget(self.driftButton,  row, 2)
        #self.driftButton.clicked.connect(self.get_drift)
        
        row += 1
        self.processButton =  QtWidgets.QPushButton()
        self.processButton.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.processButton.setText("Process")
        layout.addWidget(self.processButton,  row,0, 1, 3)
        layout.setColumnStretch(0, 3) 
        # self.scaleButton.clicked.connect(self.cursor2energy_scale)
        
        row += 1
        self.atom_sizeLabel =  QtWidgets.QLabel("atom_size")
        self.atom_sizeEdit =  QtWidgets.QLineEdit(" 100.0")
        self.atom_sizeEdit.setValidator(validfloat)
        #self.atom_sizeEdit.editingFinished.connect(self.set_energy_scale)
        self.atom_sizeUnit =  QtWidgets.QLabel("A")
        layout.addWidget(self.atom_sizeLabel,row,0)
        layout.addWidget(self.atom_sizeEdit,row,1)
        layout.addWidget(self.atom_sizeUnit,row,2)
        
        row += 1
        self.deconButton =  QtWidgets.QPushButton()
        self.deconButton.setText("LR Decon")
        self.deconButton.setCheckable(True)
        layout.addWidget(self.deconButton,  row, 0)
        self.deconButton.clicked.connect(self.decon_lr)
        
        self.atomsButton =  QtWidgets.QPushButton()
        self.atomsButton.setText("Find Atoms")
        self.atomsButton.setCheckable(True)
        layout.addWidget(self.atomsButton,  row, 1)
        self.atomsButton.clicked.connect(self.find_atoms)
        
        self.refineButton =  QtWidgets.QPushButton()
        self.refineButton.setText("Refine Atoms")
        self.refineButton.setCheckable(True)
        layout.addWidget(self.refineButton,  row, 2)
        
        return layout
        

    def update_sidebar(self):
        if '_relationship' not in self.parent.datasets:
            return
        image_list = ['None']
        image_index = 0

        if 'image' in self.parent.datasets['_relationship']:
            self.key = self.parent.datasets['_relationship']['image']
        else:
            self.key = 'None' 
            
        for index, key in enumerate(self.parent.datasets.keys()):
            if isinstance(self.parent.datasets[key], sidpy.Dataset):
                if 'IMAG' in self.parent.datasets[key].data_type.name:
                    image_list.append(f'{key}: {self.parent.datasets[key].title}')
                if key == self.key:
                    image_index = index + 1

        if image_index >len(image_list) - 1:
            image_index = len(image_list) - 1
        self.mainList.clear()
        for item in image_list:
            self.mainList.addItem(item)
        self.mainList.setCurrentIndex(image_index)
        
        self.update_image_dataset()
            
        if 'IMAG' in self.parent.dataset.data_type.name:
            dims = self.parent.dataset.get_dimensions_by_type(sidpy.DimensionType.SPATIAL, return_axis=True)
            if len(dims) <1:
                dims  = self.parent.dataset.get_dimensions_by_type(sidpy.DimensionType.RECIPROCAL, return_axis=True)
            x = dims[0]
            pixel_size_x = x[1] - x[0]
            self.atom_sizeEdit.setText(f'{pixel_size_x*4:.2f}')
            self.atom_sizeUnit.setText(x.units)
            self.atom_sizeLabel.setText('Atom size')    
        
    def update_image_dataset(self, value=0):
        self.key = self.mainList.currentText().split(':')[0]
        if self.key not in self.parent.datasets.keys():
            return
        if 'None' in self.key:
            return
        self.parent.main = self.key
        self.parent.set_dataset()
        self.dataset = self.parent.dataset
        self.parent.plotUpdate()
       
    def sum_stack(self, value=0):
        if self.dataset.data_type.name == 'IMAGE_STACK':
            dims = self.parent.dataset.get_dimensions_by_type(sidpy.DimensionType.TEMPORAL, return_axis=False)
            key =f'Sum-{self.parent.main}'
            name = f'Sum-{self.dataset.title}'
            dataset = self.parent.dataset.sum(axis=dims[0])
            dataset.metadata = self.parent.dataset.metadata.copy()
            self.add_image_dataset(key, name, dataset, data_type='IMAGE')
            
    def average_stack(self, value=0):
        if self.parent.dataset.data_type.name == 'IMAGE_STACK':
            dims = self.parent.dataset.get_dimensions_by_type(sidpy.DimensionType.TEMPORAL, return_axis=False)
            key =f'Sum-{self.parent.main}'
            name = f'Sum-{self.dataset.title}'
            dataset = self.parent.dataset.mean(axis=dims[0])
            dataset.metadata = self.parent.dataset.metadata.copy()
            self.add_image_dataset(key, name, dataset, data_type='IMAGE')
           
    def rigid_registration(self, checked):
        if self.parent.dataset.data_type.name == 'IMAGE_STACK':
            key =f'RigidReg-{self.parent.main}'
            name = f'RigidReg-{self.dataset.title}'
            dataset = image_tools.rigid_registration(self.parent.dataset)
            dataset.metadata = self.parent.dataset.metadata.copy()
            self.add_image_dataset(key, name, dataset, data_type='IMAGE_STACK')
            self.rigid_regButton.setChecked(False)

    def demon_registration(self,  value=0):
        if self.parent.dataset.data_type.name == 'IMAGE_STACK':
            key =f'DemonReg-{self.parent.main}'
            name = f'DemonReg-{self.dataset.title}'
            dataset = image_tools.demon_registration(self.parent.dataset)
            dataset.metadata = self.parent.dataset.metadata.copy()
            self.add_image_dataset(key, name, dataset, data_type='IMAGE_STACK')
            self.demon_regButton.setChecked(False)
        
    def add_image_dataset(self, key, name, dataset, data_type='IMAGE'):
        self.parent.datasets[key] = dataset
        self.parent.datasets['_relationship'][key] = key
        self.parent.datasets[key].data_type = data_type
        self.parent.datasets[key].title = name
        self.parent.datasets['_relationship']['image'] = key
        self.update_sidebar()
        
    def decon_lr(self):
        if self.parent.dataset.data_type.name != 'IMAGE':
            return
            
        if 'probe' not in self.parent.dataset.metadata.keys():
            print('decon 1')
            atom_size = float(self.atom_sizeEdit.displayText())
            if hasattr(self.dataset, 'x'):
                scale = self.parent.dataset.x[1]-self.parent.dataset.x[0]
            else:
                scale = 1.
            
            gauss_diameter = atom_size/scale
            probe = pyTEMlib.probe_tools.make_gauss(self.parent.dataset.shape[0], self.parent.dataset.shape[1], gauss_diameter)
        else:
            probe = self.parent.dataset.metadata['probe']['probe']
      
        print('Deconvolution of ', self.parent.dataset.title)
        LR_dataset = image_tools.decon_lr(self.dataset, probe, verbose=False)
        key =f'LRdeconvol-{self.parent.main}'
        name = f'LRdeconvol-{self.dataset.title}'
        self.add_image_dataset(key, name, LR_dataset, data_type='IMAGE')
        
        self.deconButton.setChecked(False)
            
    def find_atoms(self,  value=0):
        atom_size = float(self.atom_sizeEdit.displayText())
        if hasattr(self.dataset, 'x'):
            scale = self.parent.dataset.x[1]-self.parent.dataset.x[0]
        else:
            scale = 1.
        atoms = pyTEMlib.atom_tools.find_atoms(self.parent.dataset, atom_size=atom_size/scale, threshold=0.)   
        if 'atoms' not in self.parent.dataset.metadata.keys():
            self.parent.dataset.metadata['atoms'] = {}     
        self.parent.dataset.metadata['atoms']['positions'] = atoms
        self.parent.dataset.metadata['atoms']['size'] = atom_size
        self.parent.dataset.metadata['plot']['additional_features'] = 'Image'
        self.parent.plotUpdate()
        self.atomsButton.setChecked(False)
        
    def get_additional_features(self):
        if 'plot' not in self.parent.dataset.metadata.keys():
            self.parent.dataset.metadata['plot'] = {}
        if 'additional_features' not in self.parent.dataset.metadata['plot'].keys():
            self.parent.dataset.metadata['plot']['additional_features'] = []
        plot_features = {}
        if 'atoms' in self.parent.dataset.metadata:
            atoms = np.array(self.parent.dataset.metadata['atoms']['positions'])[:, :2] 
            size = self.parent.dataset.metadata['atoms']['size']
            # pg.mkPen('r', width=size)
            plot_features["atoms"] = pg.ScatterPlotItem(pos=np.array(atoms)[:,:2], pen=None , symbol='o', size=10, brush=pg.mkBrush(200,0,0,50), name='atoms')
            plot_features["atoms"].setZValue(100)
            #plot_features["atoms2"] = pg.ScatterPlotItem(pos=np.array(atoms)[:,:2]+[0,3], pen=pg.mkPen('b', width=size) , symbol='o', size=size, name='atoms')
            plot_features["atoms3"] = pg.ScatterPlotItem(pos=np.array(atoms)[:,:2]+[2,4], pen=pg.mkPen('orange', width=1) , symbol='o', size=10, name='atoms')
            
        return plot_features   

   