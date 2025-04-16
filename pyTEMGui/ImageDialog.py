#####################################################################
#
# Part of pycrosGUI
# of pycroscopy ecosystem
#
# ImageDialog: SImage processing dialog.
#       
#       
# Author: Gerd Duscher, UTK
# started 02/2025       
####################################################################
from PyQt5 import QtGui
from PyQt5 import QtWidgets
import pyqtgraph as pg

import numpy as np
import sidpy
import scipy

from pyTEMlib import image_tools
import pyTEMlib.probe_tools
import pyTEMlib.atom_tools

import skimage.feature 


class ImageDialog(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ImageDialog, self).__init__(parent)
    
        self.parent = parent
        self.set_energy = True
        layout = self.get_sidbar()
        self.atoms = None
        self.setLayout(layout)   
        self.name = 'Image'
        self.setWindowTitle("Image")

    def get_sidbar(self): 
        validfloat = QtGui.QDoubleValidator()
        
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

        self.iteration_regButton = QtWidgets.QPushButton()
        self.iteration_regButton.setText("Iterative Reg.")
        self.iteration_regButton.setCheckable(True)
        layout.addWidget(self.iteration_regButton, row, 1)
        self.iteration_regButton.clicked.connect(self.rigid_registration)

        self.phase_regButton = QtWidgets.QPushButton()
        self.phase_regButton.setText("Phase Reg.")
        self.phase_regButton.setCheckable(True)
        layout.addWidget(self.phase_regButton, row, 2)
        self.phase_regButton.clicked.connect(self.rigid_registration)

        row += 1
        self.demon_regButton =  QtWidgets.QPushButton()
        self.demon_regButton.setText("Demon Reg.")
        self.demon_regButton.setCheckable(True)
        layout.addWidget(self.demon_regButton,  row, 0)
        self.demon_regButton.clicked.connect(self.demon_registration)
        
        self.all_regButton =  QtWidgets.QPushButton()
        self.all_regButton.setText("Both Reg.")
        self.all_regButton.setCheckable(True)
        layout.addWidget(self.all_regButton,  row, 1)
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
        self.driftButton.clicked.connect(self.get_drift)
        
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
        
        self.svdButton = QtWidgets.QPushButton()
        self.svdButton.setText("Simple Clean")
        self.svdButton.setCheckable(True)
        layout.addWidget(self.svdButton,  row, 1)
        self.svdButton.clicked.connect(self.svd_clean)
        
        self.refineButton = QtWidgets.QPushButton()
        self.refineButton.setText("")
        self.refineButton.setCheckable(True)
        layout.addWidget(self.refineButton,  row, 2)
        

        row += 1
        self.processButton = QtWidgets.QPushButton()
        self.processButton.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.processButton.setText("Fourier Space")
        layout.addWidget(self.processButton,  row,0, 1, 3)
        layout.setColumnStretch(0, 3) 
        self.processButton.clicked.connect(self.adaptive_fourier_filter)
        
        row += 1
        self.fft_item =  pg.ImageItem()
        win = pg.GraphicsLayoutWidget()
        self.fft_view = win.addPlot()
        self.fft_view.addItem(self.fft_item)
        self.fft_resolution = pg.CircleROI(pos=[-.1, -.1], radius=0.1, pen=(0,9), parent=self.fft_item)
        self.fft_resolution.sigRegionChangeFinished.connect(self.fft_changed)
        
        self.fft_view.addItem(self.fft_resolution)
        
        pos = np.array([[0,0]])
        self.blobs = pg.ScatterPlotItem(pos=pos, pen=(255,0,0) , symbol='o', size=10, brush=pg.mkBrush(200,0,0,50), name='bragg')
        #self.blobs.setZValue(100)
        self.blobs.setVisible(True)
        self.low_pass= pg.ScatterPlotItem(pos=pos,  symbol='o', size=5, pen=(0,0, 255), brush=pg.mkBrush(0,0,200, 50), name='low_loss')
        #self.low_pass.setZValue(200)
        self.low_pass.setVisible(True)
        
        self.fft_view.addItem(self.blobs)
        self.fft_view.addItem(self.low_pass)
        
        layout.addWidget(win,  row,0, 1, 3)
        layout.setColumnStretch(0, 3) 
        
        row += 1
        self.low_pass_label = QtWidgets.QLabel("Low-pass")
        self.low_pass_edit = QtWidgets.QLineEdit("3")
        self.low_pass_edit.setValidator(validfloat)
        self.low_pass_edit.editingFinished.connect(self.set_resolution)
        self.low_pass_unit = QtWidgets.QLabel("1/nm")
        layout.addWidget(self.low_pass_label,row,0)
        layout.addWidget(self.low_pass_edit,row,1)
        layout.addWidget(self.low_pass_unit,row,2)
        
        
        row += 1
        self.blobThreshold_label = QtWidgets.QLabel("Threshold")
        self.blobThreshold_edit = QtWidgets.QLineEdit("0.1")
        self.blobThreshold_edit.setValidator(validfloat)
        self.blobThreshold_edit.editingFinished.connect(self.set_resolution)
        
        layout.addWidget(self.blobThreshold_label,row,0)
        layout.addWidget(self.blobThreshold_edit,row,1)
        
        self.maskButton = QtWidgets.QPushButton()
        self.maskButton.setText("Find Mask")
        self.maskButton.setCheckable(True)
        layout.addWidget(self.maskButton,  row, 2)
        self.maskButton.clicked.connect(self.add_mask)
        
        return layout
    
    def fft_changed(self, roi):
        radius = self.fft_resolution.size()[0]/2
        self.fft_resolution.sigRegionChangeFinished.disconnect()
        self.fft_resolution.setPos(pos=[-radius, -radius], update=True)
        self.resolution_edit.setText(f'{1/radius:.3f}')
        self.resolution_unit.setText(self.parent.dataset.x.units)
        self.fft_resolution.sigRegionChangeFinished.connect(self.fft_changed)
    
    def add_mask(self):
        if self.parent.dataset.data_type.name == 'IMAGE': 
            
            spot_threshold = float(self.blobThreshold_edit.displayText())
            low_pass = float(self.low_pass_edit.displayText())
            self.low_pass.setVisible(True)
            
            FOV_x = self.parent.dataset.x[-1]
            FOV_y = self.parent.dataset.y[-1]
            self.low_pass.setSize(low_pass*FOV_x)
            spots = diffractogram_spots(self.fft_mag, FOV_x, FOV_y, spot_threshold=spot_threshold)
            
            for i in range(len(spots)):
                posP =  self.fft_item.mapToParent(spots[i, 0], spots[i, 1])
                spots[i] = np.array([posP.x(), posP.y()])
            spots = spots[np.linalg.norm(spots[:,:2],axis=1)<20, :]
            spots = spots[np.linalg.norm(spots[:,:2],axis=1)>0.5, :]
            self.blobs.setData(pos=spots)
            self.blobs.setZValue(300)
            self.blobs.setVisible(True)
            self.low_pass.setVisible(True)
            self.low_pass.setZValue(300)
            self.parent.dataset.metadata['fourier'] = {'spots': spots,
                                                       'threshold': spot_threshold,
                                                       'low_path': low_pass}
            
            print('add mask')
            
            """ if self.maskButton.setChecked(True):
            self.blobs.setVisible(True)
        else:
            self.blobs.setVisible(False)"""
            
    def adaptive_fourier_filter(self):
        if 'fourier' in self.parent.dataset.metadata:
            low_pass = float(self.low_pass_edit.displayText())
            spots = self.parent.dataset.metadata['fourier']['spots']
  
            filtered_dataset = pyTEMlib.image_tools.adaptive_fourier_filter(self.parent.dataset, spots, 
                                                                    low_pass=low_pass, reflection_radius=.3)
            key =f'AFF-{self.parent.main}'
            name = f'AFF-{self.parent.dataset.title.split('-')[0]}'
            
            filtered_dataset.metadata = self.parent.dataset.metadata.copy()
            self.parent.dataset.metadata['plot']['additional_features'] = {}
            self.parent.add_image_dataset(key, name, filtered_dataset, data_type='IMAGE')
            self.blobs.setVisible(False)
            self.low_pass.setVisible(False)
            self.parent.status.showMessage('Finished adaptive Fourier filter')
        
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
        
        
    def update_fft(self):            
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
            self.fft_mag = scipy.ndimage.gaussian_filter(fft_mag, sigma=(smoothing, smoothing), order=0)
            self.fft_item.setImage(np.log2(1+self.fft_mag))
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
        self.update_fft()
        
       
    def sum_stack(self, value=0):
        if self.parent.dataset.data_type.name == 'IMAGE_STACK':
            dims = self.parent.dataset.get_dimensions_by_type(sidpy.DimensionType.TEMPORAL, return_axis=False)
            key =f'Sum-{self.parent.main}'
            name = f'Sum-{self.parent.dataset.title.split('-')[0]}'
            dataset = self.parent.dataset.sum(axis=dims[0])
            dataset.metadata = self.parent.dataset.metadata.copy()
            self.parent.dataset.metadata['plot']['additional_features'] = {}
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
        if 'Phase' in self.sender().text():
            normalization = 'phase'
            print('using phase normalization for rigid registration')
        else:
            normalization = None
            print('using cross correlation for rigid registration')
        print('using normalization', normalization, normalization==None)
        if self.parent.dataset.data_type.name == 'IMAGE_STACK':
            key =f'RigidReg-{self.parent.main.split("-")[-1]}'
            name = f'RigidReg-{self.parent.dataset.title.split("-")[-1]}'
            x = self.parent.dataset.get_image_dims(return_axis=True)[0]

            dataset = image_tools.rigid_registration(self.parent.dataset, normalization = normalization)
            dataset.metadata.update(self.parent.dataset.metadata)
            dataset.metadata
            self.parent.dataset.metadata['plot']['additional_features'] = {}
            self.parent.add_image_dataset(key, name, dataset, data_type='IMAGE_STACK')
            self.rigid_regButton.setChecked(False)
            self.parent.status.showMessage('Rigid Registration finished')
        else:
            self.parent.status.showMessage('Rigid Registration only for image stacks')

    def get_drift(self):
        if 'analysis' in self.parent.dataset.metadata:
            if 'rigid_registration' in self.parent.dataset.metadata['analysis']:
                if 'drift' in self.parent.dataset.metadata['analysis']['rigid_registration']:
                    drift = self.parent.dataset.metadata['analysis']['rigid_registration']['drift']
                    frames = np.arange(self.parent.dataset.shape[0])
                    plt = pg.plot()
                    plt.addLegend()
                    plt.plot(frames, drift[:,0],  pen='r', symbol='x', symbolPen='r',
                             symbolBrush=0.2, name='x drift')

                    plt.plot(frames, drift[:,1],  pen='b', symbol='o', symbolPen='b',
                                     symbolBrush=0.2, name='y-drift')

                    plt.setLabel('left', 'drift', units='pixel')
                    plt.setLabel('bottom',  'frames', units='#')


                    plt.setWindowTitle('drift of '+dataset.title)


    def demon_registration(self,  value=0):
        if self.parent.dataset.data_type.name == 'IMAGE_STACK':
            self.parent.status.showMessage('Demon Registration started')
            key =f'DemonReg-{self.parent.main.split("-")[-1]}'
            name = f'DemonReg-{self.parent.dataset.title.split("-")[-1]}'
            dataset = image_tools.demon_registration(self.parent.dataset)

            dataset.metadata.update(self.parent.dataset.metadata)
            self.parent.dataset.metadata['plot']['additional_features'] = {}
            self.parent.add_image_dataset(key, name, dataset, data_type='IMAGE_STACK')
            self.demon_regButton.setChecked(False)
            self.parent.status.showMessage('Demon Registration finished')
        
    def decon_lr(self):
        if self.parent.dataset.data_type.name != 'IMAGE':
            self.parent.status.showMessage(f'Deconvolution only for images only,  not  {self.parent.dataset.data_type.name}')
            return
        if 'probe' not in self.parent.dataset.metadata.keys():
            atom_size = float(self.resolution_edit.displayText())
            if hasattr(self.parent.dataset, 'x'):
                scale = self.parent.dataset.x.slope
            else:
                scale = 1.
            gauss_diameter = atom_size/scale
            if gauss_diameter < 1:
                gauss_diameter = 1.0
                gauss_diameter = 1.0
            print('gauss_diameter', gauss_diameter)
            probe = pyTEMlib.probe_tools.make_gauss(self.parent.dataset.shape[0], self.parent.dataset.shape[1], gauss_diameter)
        else:
            probe = self.parent.dataset.metadata['probe']['probe']
      
        print('Deconvolution of ', self.parent.dataset.title)
        LR_dataset = image_tools.decon_lr(self.parent.dataset, probe, verbose=False)
        key =f'LRdeconvol-{self.parent.main.split("-")[-1]}'
        name = f'LRdeconvol-{self.dataset.title.split("-")[-1]}'
        iterations = 0
        if 'Deconvolution' in LR_dataset.metadata:
            if 'Lucy-Richardson' in LR_dataset.metadata['Deconvolution']:
                iterations = LR_dataset.metadata['Deconvolution']['Lucy-Richardson']['iterations']
        self.parent.dataset.metadata['plot']['additional_features'] = {}
        
        self.parent.add_image_dataset(key, name, LR_dataset, data_type='IMAGE')
        
        self.deconButton.setChecked(False)
        if iterations >0:
            self.parent.status.showMessage(f'Lucy-Richardson deconvolution converged in {iterations} iterations')
        else:
            self.parent.status.showMessage('Lucy-Richardson deconvolution finished')
    def svd_clean(self,  value=0):
        if self.parent.dataset.data_type.name == 'IMAGE':
            
            atom_size = float(self.resolution_edit.displayText())
            if hasattr(self.parent.dataset, 'x'):
                scale = self.parent.dataset.x[1]-self.parent.dataset.x[0]
            else:
                scale = 1.
            cleaned_image = pyTEMlib.image_tools.clean_svd(self.parent.dataset, pixel_size=scale)   
            key =f"clean-{self.parent.main.split('-')[-1]}"
            name = f"clean-{self.dataset.title.split('-')[-1]}"
            self.parent.dataset.metadata['plot']['additional_features'] = {}
            self.parent.add_image_dataset(key, name, cleaned_image, data_type='IMAGE')
            self.parent.plotUpdate()
            
        self.svdButton.setChecked(False)
    
    
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

def diffractogram_spots(dset, FOV_x, FOV_y, spot_threshold=0.1):
    
    data = np.array(np.log(1+np.abs(dset)))
    data = data - data.min()
    data = data/data.max()

    # some images are strange and blob_log does not work on the power spectrum
    try:
        spots_random = skimage.feature.blob_log(data, max_sigma=5, threshold=spot_threshold)
    except ValueError:
        spots_random = skimage.feature.peak_local_max(np.array(data.T), min_distance=3, threshold_rel=spot_threshold)
        spots_random = np.hstack(spots_random, np.zeros((spots_random.shape[0], 1)))
        
    print(f'Found {spots_random.shape[0]} reflections')
    
    # Needed for conversion from pixel to Reciprocal space
    rec_scale = np.array([1/FOV_x, 1/FOV_y])
    
    spots_random[:, :2] = (spots_random[:, :2]-[data.shape[0]/2, data.shape[1]/2])
    # sort reflections
    spots_random[:, 2] = np.linalg.norm(spots_random[:, 0:2], axis=1)
    spots_index = np.argsort(spots_random[:, 2])
    
    spots = spots_random[spots_index]
    # third row is angles
    spots[:, 2] = np.arctan2(spots[:, 0], spots[:, 1])
    spots[:, :2] += [data.shape[0]/2, data.shape[1]/2]
    return spots[:, :2]
   