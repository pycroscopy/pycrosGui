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
        self.atoms = None
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
        self.resolution_label = QtWidgets.QLabel("Resolution")
        self.resolution_edit = QtWidgets.QLineEdit("0.1")
        self.resolution_edit.setValidator(validfloat)
        self.resolution_edit.editingFinished.connect(self.set_resolution)
        self.resolution_unit = QtWidgets.QLabel("A")
        layout.addWidget(self.resolution_label,row,0)
        layout.addWidget(self.resolution_edit,row,1)
        layout.addWidget(self.resolution_unit,row,2)
        
        row += 1
        self.deconButton = QtWidgets.QPushButton()
        self.deconButton.setText("LR Decon")
        self.deconButton.setCheckable(True)
        layout.addWidget(self.deconButton,  row, 0)
        self.deconButton.clicked.connect(self.decon_lr)
        
        self.atomsButton = QtWidgets.QPushButton()
        self.atomsButton.setText("Find Atoms")
        self.atomsButton.setCheckable(True)
        layout.addWidget(self.atomsButton,  row, 1)
        self.atomsButton.clicked.connect(self.find_atoms)
        
        self.refineButton = QtWidgets.QPushButton()
        self.refineButton.setText("Refine Atoms")
        self.refineButton.setCheckable(True)
        layout.addWidget(self.refineButton,  row, 2)
        

        row += 1
        self.processButton = QtWidgets.QPushButton()
        self.processButton.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.processButton.setText("Fourier Space")
        layout.addWidget(self.processButton,  row,0, 1, 3)
        layout.setColumnStretch(0, 3) 
        
        row += 1
        self.fft_item =  pg.ImageItem()
        win = pg.GraphicsLayoutWidget()
        self.fft_view = win.addPlot()
        self.fft_view.addItem(self.fft_item)
        self.fft_resolution = pg.CircleROI(pos=[-.1, -.1], radius=0.1, pen=(0,9), parent=self.fft_item)
        self.fft_resolution.sigRegionChangeFinished.connect(self.fft_changed)
        
        self.fft_view.addItem(self.fft_resolution)
        
        layout.addWidget(win,  row,0, 1, 3)
        layout.setColumnStretch(0, 3) 
        return layout
    
    def fft_changed(self, roi):
        radius = self.fft_resolution.size()[0]/2
        self.fft_resolution.sigRegionChangeFinished.disconnect()
        self.fft_resolution.setPos(pos=[-radius, -radius], update=True)
        self.resolution_edit.setText(f'{1/radius:.2f}')
        self.resolution_unit.setText(self.parent.dataset.x.units)
        self.fft_resolution.sigRegionChangeFinished.connect(self.fft_changed)

    def set_resolution(self):
        resolution = 1/float(self.resolution_edit.displayText())
        self.fft_resolution.setSize([resolution*2, resolution*2])
        self.resolution_unit.setText(self.parent.dataset.x.units)
        
        
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
            
            smoothing = 1
            print('update fft')
            if self.parent.dataset.data_type.name == 'IMAGE_STACK':
                new_image = np.array(self.parent.dataset.mean(axis=0))
            else:
                new_image = np.array(self.parent.dataset)
            new_image -= new_image.min()
            fft_transform = (np.fft.fftshift(np.fft.fft2(new_image)))
            fft_mag = np.abs(fft_transform)
            fft_mag2 = scipy.ndimage.gaussian_filter(fft_mag, sigma=(smoothing, smoothing), order=0)
            self.fft_item.setImage(np.log2(1+fft_mag2))
            self.fft_view.setAspectLocked(True)

            tr = QtGui.QTransform()  # prepare ImageItem transformation:
            tr.scale(1/self.parent.dataset.x[-1], 1/self.parent.dataset.y[-1])       # scale horizontal and vertical axes
            tr.translate(-len(self.parent.dataset.x)/2, -len(self.parent.dataset.y)/2) # move 3x3 image to locate center at axis origin
            self.fft_item.setTransform(tr) # assign transform
           
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
        if self.parent.dataset.data_type.name == 'IMAGE_STACK':
            dims = self.parent.dataset.get_dimensions_by_type(sidpy.DimensionType.TEMPORAL, return_axis=False)
            key =f'Sum-{self.parent.main}'
            name = f'Sum-{self.parent.dataset.title.split('-')[0]}'
            dataset = self.parent.dataset.sum(axis=dims[0])
            dataset.metadata = self.parent.dataset.metadata.copy()
            self.parent.metadata['plot']['additional_features'] = {}
            self.parent.add_image_dataset(key, name, dataset, data_type='IMAGE')
            
    def average_stack(self, value=0):
        if self.parent.dataset.data_type.name == 'IMAGE_STACK':
            dims = self.parent.dataset.get_dimensions_by_type(sidpy.DimensionType.TEMPORAL, return_axis=False)
            key =f'Sum-{self.parent.main}'
            name = f'Sum-{self.dataset.title.split('-')[0]}'
            dataset = self.parent.dataset.mean(axis=dims[0])
            dataset.metadata = self.parent.dataset.metadata.copy()
            
            self.parent.add_image_dataset(key, name, dataset, data_type='IMAGE')
            
    def rigid_registration(self, checked):
        if self.parent.dataset.data_type.name == 'IMAGE_STACK':
            key =f'RigidReg-{self.parent.main.split("-")[-1]}'
            name = f'RigidReg-{self.parent.dataset.title.split("-")[-1]}'
            dataset = image_tools.rigid_registration(self.parent.dataset)
            dataset.metadata.update(self.parent.dataset.metadata)
            self.parent.metadata['plot']['additional_features'] = {}
            self.parent.add_image_dataset(key, name, dataset, data_type='IMAGE_STACK')
            self.rigid_regButton.setChecked(False)

    def demon_registration(self,  value=0):
        if self.parent.dataset.data_type.name == 'IMAGE_STACK':
            key =f'DemonReg-{self.parent.main.split("-")[-1]}'
            name = f'DemonReg-{self.parent.dataset.title.split("-")[-1]}'
            dataset = image_tools.demon_registration(self.parent.dataset)
            dataset.metadata.update(self.parent.dataset.metadata)
            self.parent.metadata['plot']['additional_features'] = {}
            self.parent.add_image_dataset(key, name, dataset, data_type='IMAGE_STACK')
            self.demon_regButton.setChecked(False)
        
    def decon_lr(self):
        if self.parent.dataset.data_type.name != 'IMAGE':
            return
        if 'probe' not in self.parent.dataset.metadata.keys():
            atom_size = float(self.resolution_edit.displayText())*2
            if hasattr(self.parent.dataset, 'x'):
                scale = self.parent.dataset.x[1]-self.parent.dataset.x[0]
            else:
                scale = 1.
            gauss_diameter = atom_size/scale
            if gauss_diameter < 3:
                gauss_diameter = 3.0
            print('gauss_diameter', gauss_diameter)
            probe = pyTEMlib.probe_tools.make_gauss(self.parent.dataset.shape[0], self.parent.dataset.shape[1], gauss_diameter)
        else:
            probe = self.parent.dataset.metadata['probe']['probe']
      
        print('Deconvolution of ', self.parent.dataset.title)
        LR_dataset = image_tools.decon_lr(self.parent.dataset, probe, verbose=False)
        print(LR_dataset, LR_dataset.min(), LR_dataset.max()) 
        key =f'LRdeconvol-{self.parent.main.split("-")[-1]}'
        name = f'LRdeconvol-{self.dataset.title.split("-")[-1]}'
        self.parent.metadata['plot']['additional_features'] = {}
        
        self.parent.add_image_dataset(key, name, LR_dataset, data_type='IMAGE')
        
        self.deconButton.setChecked(False)
            
    def find_atoms(self,  value=0):
        atom_size = float(self.resolution_edit.displayText())
        if hasattr(self.parent.dataset, 'x'):
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
            pos = np.array(atoms)[:,:2]
            for i in range(len(atoms)):
                posP =  self.parent.img.mapToParent(atoms[i, 0], atoms[i, 1])
                pos[i] = np.array([posP.x(), posP.y()])
            plot_features["atoms"] = pos
        return plot_features   

   