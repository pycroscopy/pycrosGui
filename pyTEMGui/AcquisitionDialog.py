#####################################################################
#
# Part of pycrosGui
#
# AcquistionDialog: Acquisition directly from Microcope.
#       
#####################################################################
from PyQt5 import QtGui
from PyQt5 import QtWidgets


import numpy as np
import sidpy
import scipy

from pyTEMlib import eels_tools
import sys
sys.path.insert(0,'/lustre/isaac24/proj/UTK0286/STEM_TF/Autoscript/autoscript_code_lib/')
acquistion_enabled = True
try:
    from autoscript_tem_microscope_client import TemMicroscopeClient
    from autoscript_tem_microscope_client.enumerations import *
    from autoscript_tem_microscope_client.structures import *
except:
    acquistion_enabled = False


"""
from autoscript_tem_microscope_client import TemMicroscopeClient
from autoscript_tem_microscope_client.enumerations import *
from autoscript_tem_microscope_client.structures import *

microscope = TemMicroscopeClient()
ip = ""
if ip == "":
    ip = input("Please enter the IP address of the microscope: ")
    
ip_TF": "10.46.217.241", 
"port_TF": 9095,
"ip_TF_sim": "10.46.217.242", 
"port_TF_sim": 9090
microscope = TemMicroscopeClient()
microscope.connect(ip)
print("Connected to the microscope")

haadf_image = microscope.acquisition.acquire_stem_image(DetectorType.HAADF, 128, 4e-6)# haadf is pixel wise


"""

#from DTMicroscope.base.stem import DTSTEM

class AcquDialog(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(AcquDialog, self).__init__(parent)
    
        self.parent = parent
        self.set_energy = True
        layout = self.get_sidbar()
        self.setLayout(layout)    
        self.name = 'Acquisition'
        self.setWindowTitle(self.name)
        
        self.number = 0
        self.parent.acquisition_enabled = acquistion_enabled

    def get_sidbar(self): 
        validfloat = QtGui.QDoubleValidator()
        validint = QtGui.QIntValidator()

        layout = QtWidgets.QGridLayout()
        row = 0
        self.experimentButton = QtWidgets.QPushButton()
        self.experimentButton.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.experimentButton.setText("Acquisition")
        self.experimentButton.clicked.connect(self.acquire)
        layout.addWidget(self.experimentButton,  row,0, 1, 3)
        layout.setColumnStretch(0, 3)      
        
        row += 1
        self.nFramesLabel = QtWidgets.QLabel("Series")
        self.nFramesEdit = QtWidgets.QLineEdit("1")
        self.nFramesEdit.setValidator(validint)
        self.nFramesEdit.editingFinished.connect(self.OnExposeEnter)
        self.nFramesUnit = QtWidgets.QLabel("frames")
        layout.addWidget(self.nFramesLabel,row,0)
        layout.addWidget(self.nFramesEdit,row,1)
        layout.addWidget(self.nFramesUnit,row,2)

        row += 1
        self.defocusLabel = QtWidgets.QLabel("df series")
        self.defocusEdit = QtWidgets.QLineEdit("0")
        self.defocusEdit.setValidator(validint)
        # self.defocusEdit.editingFinished.connect(self.OnExposeEnter)
        self.defocusUnit = QtWidgets.QLabel("nm")
        layout.addWidget(self.defocusLabel, row, 0)
        layout.addWidget(self.defocusEdit, row, 1)
        layout.addWidget(self.defocusUnit, row, 2)
        
        row += 1
        self.timeLabel = QtWidgets.QLabel("Exp. Time")
        self.timeEdit = QtWidgets.QLineEdit(" 4")
        
        self.timeEdit.setValidator(validint)
        self.timeEdit.editingFinished.connect(self.OnExposeEnter)
        self.timeUnit = QtWidgets.QLabel("μs")
        layout.addWidget(self.timeLabel,row,0)
        layout.addWidget(self.timeEdit,row,1)
        layout.addWidget(self.timeUnit,row,2)

        row += 1
        self.convLabel = QtWidgets.QLabel("Size")
        self.convEdit = QtWidgets.QLineEdit(" 512")
        self.convEdit.setValidator(validfloat)
        self.convEdit.editingFinished.connect(self.OnConvEnter)
        self.convUnit = QtWidgets.QLabel("pixels")
        layout.addWidget(self.convLabel,row,0)
        layout.addWidget(self.convEdit,row,1)
        layout.addWidget(self.convUnit,row,2)

        row += 1
        self.fovLabel = QtWidgets.QLabel("FOV")
        self.fovEdit = QtWidgets.QLineEdit(" 10.0")
        self.fovEdit.setValidator(validfloat)
        self.fovUnit = QtWidgets.QLabel("nm")
        layout.addWidget(self.fovLabel,row,0)
        layout.addWidget(self.fovEdit,row,1)
        layout.addWidget(self.fovUnit,row,2)
        
        row += 1
        self.collLabel = QtWidgets.QLabel("Current")
        self.collEdit = QtWidgets.QLineEdit(" 10.0")
        self.collEdit.setValidator(validfloat)
        self.collEdit.editingFinished.connect(self.OnCollEnter)
        self.collUnit = QtWidgets.QLabel("pA")
        layout.addWidget(self.collLabel,row,0)
        layout.addWidget(self.collEdit,row,1)
        layout.addWidget(self.collUnit,row,2)


        row += 1
        self.quantifyButton = QtWidgets.QPushButton()
        self.quantifyButton.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.quantifyButton.setText("Detector")
        layout.addWidget(self.quantifyButton,  row,0, 1, 3)
        layout.setColumnStretch(0, 3)        
        
        row += 1 
        self.detectorList = QtWidgets.QListWidget()
        self.detectorList.addItem("HAADF")
        self.detectorList.addItem("MAADF")
        self.detectorList.addItem("EDS")
        self.detectorList.addItem("EELS")
        self.detectorList.addItem("BF")
        self.detectorList.addItem("FluCam")
        self.detectorList.addItem("Ceta")
        self.detectorList.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        
        layout.addWidget(self.detectorList,  row,0, 1, 3)
        layout.setColumnStretch(1, 3)  
        self.detectorList.itemClicked.connect(self.selectDetectors)
        
        row += 1
        self.get_shiftButton = QtWidgets.QPushButton()
        self.get_shiftButton.setText("C1/A1")
        self.get_shiftButton.setCheckable(True)
        layout.addWidget(self.get_shiftButton,  row, 0)
        self.get_shiftButton.clicked.connect(self.get_shift)

        self.set_shiftButton = QtWidgets.QPushButton()
        self.set_shiftButton.setText(" Auto Gain")
        self.set_shiftButton.setCheckable(True)
        layout.addWidget(self.set_shiftButton,  row, 2)
        self.set_shiftButton.setDisabled(True)
        self.set_shiftButton.clicked.connect(self.shift_spectrum)

        row += 1
        self.gainLabel = QtWidgets.QLabel("Gain")
        self.gainEdit = QtWidgets.QLineEdit(" 1")
        self.gainEdit.setValidator(validfloat)
        self.gainEdit.editingFinished.connect(self.OnFlux_ppmEnter)
        # self.flux_ppmUnit = QtWidgets.QLabel("%")
        layout.addWidget(self.gainLabel,row,0)
        layout.addWidget(self.gainEdit,row,1)
        #layout.addWidget(self.flux_ppmUnit,row,2)
        
        self.autoGainButton = QtWidgets.QPushButton()
        self.autoGainButton.setText(" Auto Gain")
        self.autoGainButton.setCheckable(True)
        layout.addWidget(self.autoGainButton,  row, 2)
        self.autoGainButton.setDisabled(True)
        self.autoGainButton.clicked.connect(self.shift_spectrum)
        
       
        row += 1
        self.microscopeButton = QtWidgets.QPushButton()
        self.microscopeButton.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.microscopeButton.setText("Microscope")
        layout.addWidget(self.microscopeButton,  row,0, 1, 3)
        self.microscopeButton.clicked.connect(self.print_mic_stage_position)
        layout.setColumnStretch(0, 3)     
        
        return layout
        
    def selectDetectors(self, ch):
        currentDetector = self.detectorList.currentItem().text()
        
        if currentDetector == 'BF':
            impossible_detector_indices = [3,5,6]
        elif currentDetector == 'FluCam':
            impossible_detector_indices = [3,4,6]
        elif currentDetector == 'Ceta':
            impossible_detector_indices = [3,4,5]
        else:
            impossible_detector_indices = []
        
                
        
        items = self.detectorList.selectedItems()
        
        for i in impossible_detector_indices:
            self.detectorList.items(i).setSelected(False)
        x = []
        for i in range(len(items)):
            x.append(str(self.detectorList.selectedItems()[i].text()))
       

        print (x)
        
    def acquire(self):
        fov  = float(self.fovEdit.displayText())
        #self.microscope.optics['fov'] = fov
        # if self.DetectorType
        self.microscope = self.parent.microscope
        image = self.microscope.acquisition.acquire_stem_image(DetectorType.HAADF, 128, 4e-6)# haadf is pixel wise

        print(dir(image.metadata))
        #image = self.microscope.get_scanned_image(size=512, dwell_time=1, detector='haadf', seed=42)
        self.make_dataset(image.data)
        
        self.parent.datasets[f'Acquired_{self.number:03d}'] = self.dataset
        
        self.parent.dataset = self.dataset
        self.parent.main = f'Acquired_{self.number:03d}'
        self.number += 1
        if '_relationship' not in self.parent.datasets:
            self.parent.datasets['_relationship'] = {}
        self.parent.update_DataDialog()
        
        
        self.parent.add_image_dataset(f'Acquired_{self.number:03d}', 'HAADF', self.dataset, data_type='IMAGE')
        
        self.parent.dataset.metadata['plot']= {'additional_features': {}}
        self.experimentButton.setChecked(False)
        self.parent.status.showMessage('Acquired Image')
        
    def make_dataset(self, image):
        
        dataset = sidpy.Dataset.from_array(image)
        dataset.data_type = 'Image'
        dataset.title = 'HAADF'
        fov  = float(self.fovEdit.displayText())
        dataset.set_dimension(0, sidpy.Dimension(np.arange(dataset.shape[0])*fov/dataset.shape[0], 
                                          name='x', units='nm', quantity='Length',
                                          dimension_type='spatial'))
        dataset.set_dimension(1, sidpy.Dimension(np.arange(dataset.shape[1])*fov/dataset.shape[1],
                                          'y', units='nm', quantity='Length',
                                          dimension_type='spatial'))
        self.dataset = dataset
    
    def set_dataset(self):
        item_text = self.mainList.currentText()
        self.parent.main = item_text.split(':')[0]
        
    def print_mic_stage_position(self):
        position = self.microscope.specimen.stage.position
        pos_dict = {"x": position.x, "y": position.y, "z": position.z, "alpha": position.a, "beta": position.b}
        print(pos_dict)

    def set_flux(self, value=0):
        if self.referenceList.currentText() == 'None':
            self.parent.datasets[self.parent.key].metadata['experiment']['flux_ppm'] = 0.
        else:
            
            reference_key = self.referenceList.currentText().split(':')[0]
            self.parent.datasets['_relationship']['reference'] = reference_key
            if 'SPEC' in self.parent.datasets[reference_key].data_type.name:
                self.parent.datasets['_relationship']['low_loss'] = reference_key
                self.parent.lowloss_key = reference_key
                spectrum_dimensions = self.parent.dataset.get_spectral_dims()

                number_of_pixels = 1
                for index, dimension in enumerate(self.parent.dataset.shape):
                    if index not in spectrum_dimensions:
                        number_of_pixels *= dimension
                if self.parent.datasets[reference_key].metadata['experiment']['exposure_time'] == 0.0:
                    if self.parent.datasets[reference_key].metadata['experiment']['single_exposure_time'] == 0.0:
                        return
                    else:
                        self.parent.datasets[reference_key].metadata['experiment']['exposure_time'] = (self.parent.datasets[reference_key].metadata['experiment']['single_exposure_time'] *
                                                                                     self.parent.datasets[reference_key].metadata['experiment']['number_of_frames'])

                self.parent.datasets[self.parent.main].metadata['experiment']['flux_ppm'] = ((np.array(self.parent.datasets[reference_key])*1e-6).sum() /
                                                                          self.parent.datasets[reference_key].metadata['experiment']['exposure_time'] /
                                                                          number_of_pixels)
                self.parent.datasets[self.parent.main].metadata['experiment']['flux_ppm'] *= self.parent.datasets[self.parent.main].metadata['experiment']['exposure_time']
            if 'SPECT' in self.parent.datasets[reference_key].data_type.name:
                pass # self.info_tab[14, 0].disabled = False
            self.flux_ppmEdit.setText(f"{self.parent.datasets[self.parent.main].metadata['experiment']['flux_ppm']:.2f}")
        
    def update_sidebar(self):
        # self.updateInfo()
        pass
    def updateInfo(self):
        if '_relationship' not in self.parent.datasets:
            return
        spectrum_list = ['None']
        data_list = []
        
        self.key = self.info_key = self.parent.main
        self.parent.set_dataset()
        main_index = 0
        
        
        if 'reference' in self.parent.datasets['_relationship']:
            reference_key = self.parent.datasets['_relationship']['reference']
        else:
            reference_key = 'None'
        reference_index = 0
        for key in self.parent.datasets.keys():
            if isinstance(self.parent.datasets[key], sidpy.Dataset):
                if key[0] != '_' :
                    data_list.append(f'{key}: {self.parent.datasets[key].title}')
                    if 'SPECTR' in self.parent.datasets[key].data_type.name:
                        spectrum_list.append(f'{key}: {self.parent.datasets[key].title}')
                    if key == reference_key:
                        reference_index = len(data_list)                  
                    if key == self.key:
                        main_index = len(data_list)-1
                   
        self.mainList.clear()
        for item in data_list:
            self.mainList.addItem(item)
        self.mainList.setCurrentIndex(main_index)
        
        self.referenceList.clear()
        self.referenceList.addItem('None')
        for item in data_list:
            self.referenceList.addItem(item)
        self.referenceList.setCurrentIndex(reference_index)
            
        if 'SPECTR' in self.parent.dataset.data_type.name:
            energy_scale = self.parent.datasets[self.key].get_spectral_dims(return_axis=True)[0]
            
            self.offsetEdit.setText(f'{energy_scale[0]:.3f}')
            self.offsetUnit.setText('eV')
            self.offsetLabel.setText('Offset')
            disp = energy_scale[1] - energy_scale[0]
            self.dispersionEdit.setText(f'{disp:.3f}')
            self.dispersionUnit.setText('eV')
            self.dispersionLabel.setText('Dispersion')
        elif 'IMAGE' in self.parent.dataset.data_type.name:
            pixel_size_x = self.parent.dataset.x[1] - self.parent.dataset.x[0]
            self.offsetEdit.setText(f'{pixel_size_x:.3f}')
            self.offsetUnit.setText('nm')
            self.offsetLabel.setText('Pixel size x')
            pixel_size_y = self.parent.dataset.y[1] - self.parent.dataset.y[0]
            self.dispersionEdit.setText(f'{pixel_size_y:.3f}')
            self.dispersionUnit.setText('nm')
            self.dispersionLabel.setText('Pixel size y')    

        
        if 'experiment' in self.parent.dataset.metadata:
            if 'exposure_time' in self.parent.dataset.metadata['experiment']:
                self.timeEdit.setText(f"{self.parent.dataset.metadata['experiment']['exposure_time']:.3f}")
                self.timeUnit.setText('s')
            else:
                self.timeEdit.setText('0')
            if 'convergence_angle' in self.parent.dataset.metadata['experiment']:
                self.convEdit.setText(f"{self.parent.dataset.metadata['experiment']['convergence_angle']*1000:.1f}")
            else:
                self.convEdit.setText('0')
            if 'collection_angle' in self.parent.dataset.metadata['experiment']:
                col_angle = self.parent.dataset.metadata['experiment']['collection_angle']*1000
                if 'collection_angle_end' in self.parent.dataset.metadata['experiment']:
                    col_angle_end = self.parent.dataset.metadata['experiment']['collection_angle_end']*1000
                    self.collEdit.setText(f"{col_angle:.1f}-{col_angle_end:.1f}")
                else:
                    self.collEdit.setText(f"{col_angle:.1f}")
            else:
                self.collEdit.setText('0')
            if 'acceleration_voltage' in self.parent.dataset.metadata['experiment']:
                self.E0Edit.setText(f"{self.parent.dataset.metadata['experiment']['acceleration_voltage']/1000:.1f}")

            if 'current' in self.parent.dataset.metadata['experiment']:
                current = self.parent.dataset.metadata['experiment']['current']
                self.VOAEdit.setText(f"{current*1e12:.2f}")
                self.fluxEdit.setText(f"{current/scipy.constants.elementary_charge:.3f}")
                if 'pixel_time'in self.parent.dataset.metadata['experiment']:
                    pixel_time = self.parent.dataset.metadata['experiment']['pixel_time']
                    self.flux_ppmEdit.setText(f"{current//scipy.constants.elementary_charge*pixel_time:.1f}")
                    self.flux_ppmUnit.setText('e<sup>-</sup>/pixel')
        else:
            self.parent.dataset.metadata['experiment'] = {}

        if self.parent.intensity_scale == 1.0:
            self.quantifyButton.setChecked(False)
        else:
            self.quantifyButton.setChecked(True)
        
        self.parent.plotUpdate()
       
    def cursor2energy_scale(self, value):
        self.energy_scale = self.parent.dataset.get_spectral_dims(return_axis=True)[0]
        dispersion = float(self.parent.right_cursor_value.displayText())-float(self.parent.left_cursor_value.displayText())
        values = self.parent.cursor.getRegion()
        
        start_channel = np.searchsorted(self.energy_scale, values[0])
        end_channel = np.searchsorted(self.energy_scale, values[1])
 
        dispersion /= (end_channel - start_channel)
        offset = float(self.parent.left_cursor_value.displayText()) - start_channel * dispersion
        self.offsetEdit.setText(f'{offset:.3f}')
        self.dispersionEdit.setText(f'{dispersion:.3f}')
        self.set_scale()

   
    def set_scale(self, value=0):
        if 'SPEC' in self.parent.dataset.data_type.name:
            self.energy_scale = self.parent.datasets[self.key].get_spectral_dims(return_axis=True)[0]
            dispersion = self.parent.datasets[self.key].get_dimension_slope(self.energy_scale)
            self.energy_scale *= (float(self.dispersionEdit.displayText()) / dispersion)
            self.energy_scale += (float(self.offsetEdit.displayText()) - self.energy_scale[0])
            self.parent.plotUpdate()
        elif 'IMAGE' in self.parent.dataset.data_type.name:
            pixel_size_x = float(self.dispersionEdit.displayText())
            pixel_size_y = float(self.offsetEdit.displayText())
            image_dims = self.parent.dataset.get_image_dims()
            self.parent.dataset.set_dimension(image_dims[0], sidpy.Dimension(np.arange(self.parent.dataset.shape[image_dims[0]])*pixel_size_x, 
                                                                             name='x', units='nm', quantity='Length', 
                                                                             dimension_type='spatial'))
            self.parent.dataset.set_dimension(image_dims[1], sidpy.Dimension(np.arange(self.parent.dataset.shape[image_dims[1]])*pixel_size_y, 
                                                                              name='y', units='nm', quantity='Length',
                                                                              dimension_type='spatial'))
            self.parent.plotUpdate()
    
    def set_intensity_scale(self, checked):
        self.parent.intensity_scale = 1.0
        if checked:
            if 'experiment' in self.parent.dataset.metadata:
                if 'flux_ppm' in self.parent.dataset.metadata['experiment']:
                    if 'SPEC' in self.parent.dataset.data_type.name:
                       energy_scale = self.parent.dataset.get_spectral_dims(return_axis=True)[0]
                       dispersion = energy_scale[1]-energy_scale[0]
                    else:
                        dispersion = 1.0
                        
                    self.parent.intensity_scale = dispersion/self.parent.dataset.metadata['experiment']['flux_ppm']
        self.parent.plotUpdate()

    def get_shift(self,  value=0):
        if 'low_loss' in self.parent.datasets['_relationship']:
            low_loss = self.parent.datasets[self.parent.datasets['_relationship']['low_loss']]

            self.parent.datasets['shifted_low_loss']  = eels_tools.align_zero_loss(low_loss)
            self.parent.datasets['shifted_low_loss'].title = self.parent.dataset.title + '_shifted'
            self.parent.datasets['_relationship']['low_loss'] = 'shifted_low_loss'
            self.updateInfo()
           
        if 'low_loss' in self.parent.datasets['_relationship']:
            if 'zero_loss' in self.parent.datasets[self.parent.datasets['_relationship']['low_loss']].metadata:
                if 'shifted' in self.parent.datasets[self.parent.datasets['_relationship']['low_loss']].metadata['zero_loss'].keys():
                    self.set_shiftButton.setDisabled(False)
    
    def shift_spectrum(self,  value=0):
        shifts = self.parent.dataset.shape
        if 'low_loss' in self.parent.datasets['_relationship']:
            if 'zero_loss' in self.parent.datasets[self.parent.datasets['_relationship']['low_loss']].metadata:
                if 'shifted' in self.parent.datasets[self.parent.datasets['_relationship']['low_loss']].metadata['zero_loss'].keys():
                    shifts = self.parent.datasets[self.parent.datasets['_relationship']['low_loss']].metadata['zero_loss']['shifted']
                    shifts_new = shifts.copy()
                    if 'zero_loss' in self.parent.dataset.metadata:
                        if 'shifted' in self.parent.dataset.metadata['zero_loss'].keys():
                            shifts_new = shifts-self.parent.dataset.metadata['zero_loss']['shifted']
                    else:
                        self.parent.dataset.metadata['zero_loss'] = {}
                    
                    self.parent.dataset = eels_tools.shift_energy(self.parent.dataset, shifts_new)
                    self.parent.dataset.metadata['zero_loss']['shifted'] = shifts
                    self.parent.plotUpdate()         
   
        
    def OnExposeEnter(self):
        self.parent.dataset.metadata['experiment']['exposure_time'] = float(self.timeEdit.displayText())
       
    def OnCollEnter(self):
        self.parent.dataset.metadata['experiment']['collection_angle'] = float(self.collEdit.displayText())
       
    def OnConvEnter(self):
        self.parent.dataset.metadata['experiment']['convergence_angle']=float(self.convEdit.displayText())
        
    def OnE0Enter(self):
        self.parent.dataset.metadata['experiment']['acceleration_voltage'] = float(self.E0Edit.displayText()) * 1000.
       
    def OnConversionEnter(self):
        self.parent.dataset.metadata['experiment']['counts_conversion'] = float(self.conversionEdit.displayText())
       
    def OnFlux_ppmEnter(self):
        self.parent.dataset.metadata['experiment']['flux_ppm'] = float(self.flux_ppmEdit.displayText())
        
    def OnFluxEnter(self):
        flux = float(self.fluxEdit.displayText()) 
        self.parent.dataset.metadata['experiment']['flux'] = flux
        
        current = flux * (scipy.constants.e*1e12)
        self.VOAEdit.displayText(f"{current:.2f}")
        
    def OnVOAEnter(self):
        self.parent.dataset.metadata['experiment']['camera_current'] = float(self.VOAEdit.displayText()) 
        flux = float(self.VOAEdit.displayText())/(scipy.constants.e*1e12)
        self.fluxEdit.setText(f"{flux:.2f}")
        self.parent.dataset.metadata['experiment']['flux'] = flux