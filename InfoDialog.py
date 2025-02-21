#####################################################################
#
# Part of Quantifit
#
# SpecInfoDialog: Spectrum information dialog.
#       - Name
#       - Disperison
#       - Offset
#       - Exposure Time
#       - Acceleration Voltage
#       - Collection Angle
#       - Convergence Angle
#       - Binning
#       - Conversion Factor for CCD
#       - Flux of incident beam in #e- per second
#       - VOA: current of a secondary measure of beam current in nA
#           (here virtual objective aperture)
#           ** changed to reflect Libra and pA ** Nov 2012
#       
#####################################################################
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import numpy as np
import sidpy
import scipy

from pyTEMlib import eels_tools


class InfoDialog(QWidget):
    def __init__(self, parent=None):
        super(InfoDialog, self).__init__(parent)
    
        self.parent = parent
        self.set_energy = True
        layout = self.get_sidbar()
        self.setLayout(layout)    
        self.setWindowTitle("Info")

    def get_sidbar(self): 
        validfloat = QDoubleValidator()
        validint = QIntValidator()        
        
        layout = QGridLayout()
        row = 0 
        self.mainList = QComboBox(self)
        self.mainList.addItem("None")
        layout.addWidget(self.mainList,  row,0, 1, 3)
        layout.setColumnStretch(0, 3)  

        self.mainList.activated[str].connect(self.set_dataset)
        
        row += 1
        self.scaleButton = QPushButton()
        self.scaleButton.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.scaleButton.setText("Scale")
        layout.addWidget(self.scaleButton,  row,0, 1, 3)
        layout.setColumnStretch(0, 3) 
        self.scaleButton.clicked.connect(self.cursor2energy_scale)
        
        row += 1
        self.offsetLabel = QLabel("Offset")
        self.offsetEdit = QLineEdit(" 100.0")
        self.offsetEdit.setValidator(validfloat)
        self.offsetEdit.editingFinished.connect(self.set_energy_scale)
        self.offsetUnit = QLabel("eV")
        layout.addWidget(self.offsetLabel,row,0)
        layout.addWidget(self.offsetEdit,row,1)
        layout.addWidget(self.offsetUnit,row,2)
        
        row += 1
        self.dispersionLabel = QLabel("Dispersion")
        self.dispersionEdit = QLineEdit(" 100.0")
        self.dispersionEdit.setValidator(validfloat)
        self.dispersionEdit.editingFinished.connect(self.set_energy_scale)
        self.dispersionUnit = QLabel("eV")
        layout.addWidget(self.dispersionLabel,row,0)
        layout.addWidget(self.dispersionEdit,row,1)
        layout.addWidget(self.dispersionUnit,row,2)
        
        row += 1
        self.experimentButton = QPushButton()
        self.experimentButton.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.experimentButton.setText("Experimental Conditions")
        layout.addWidget(self.experimentButton,  row,0, 1, 3)
        layout.setColumnStretch(0, 3)        
        
        row += 1
        self.timeLabel = QLabel("Exp. Time")
        self.timeEdit = QLineEdit(" 100.0")
        self.timeEdit.setValidator(validfloat)
        self.timeEdit.editingFinished.connect(self.OnExposeEnter)
        self.timeUnit = QLabel("ms")
        layout.addWidget(self.timeLabel,row,0)
        layout.addWidget(self.timeEdit,row,1)
        layout.addWidget(self.timeUnit,row,2)

        row += 1
        self.convLabel = QLabel("Conv. Angle")
        self.convEdit = QLineEdit(" 100.0")
        self.convEdit.setValidator(validfloat)
        self.convEdit.editingFinished.connect(self.OnConvEnter)
        self.convUnit = QLabel("mrad")
        layout.addWidget(self.convLabel,row,0)
        layout.addWidget(self.convEdit,row,1)
        layout.addWidget(self.convUnit,row,2)

        row += 1
        self.collLabel = QLabel("Coll. Angle")
        self.collEdit = QLineEdit(" 10.0")
        self.collEdit.setValidator(validfloat)
        self.collEdit.editingFinished.connect(self.OnCollEnter)
        self.collUnit = QLabel("mrad")
        layout.addWidget(self.collLabel,row,0)
        layout.addWidget(self.collEdit,row,1)
        layout.addWidget(self.collUnit,row,2)

        row += 1
        self.E0Label = QLabel("Acc. Voltage")
        self.E0Edit = QLineEdit(" 100.0")
        self.E0Edit.setValidator(validfloat)
        self.E0Edit.editingFinished.connect(self.OnE0Enter)
        self.E0Unit = QLabel("kV")
        layout.addWidget(self.E0Label,row,0)
        layout.addWidget(self.E0Edit,row,1)
        layout.addWidget(self.E0Unit,row,2)

        row += 1
        self.quantifyButton = QPushButton()
        self.quantifyButton.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.quantifyButton.setText("Quantification")
        
        self.quantifyButton.setCheckable(True)
        self.quantifyButton.clicked.connect(self.set_intensity_scale)
        layout.addWidget(self.quantifyButton,  row,0, 1, 3)
        layout.setColumnStretch(0, 3)        
        
        row += 1 
        self.referenceList = QComboBox(self)
        self.referenceList.addItem("None")
        layout.addWidget(self.referenceList,  row,0, 1, 3)
        layout.setColumnStretch(0, 3)  
        self.referenceList.activated[str].connect(self.set_flux)
        
        row += 1
        self.get_shiftButton = QPushButton()
        self.get_shiftButton.setText("Get Shift")
        self.get_shiftButton.setCheckable(True)
        layout.addWidget(self.get_shiftButton,  row, 0)
        self.get_shiftButton.clicked.connect(self.get_shift)

        self.set_shiftButton = QPushButton()
        self.set_shiftButton.setText("Shift Spectrum")
        self.set_shiftButton.setCheckable(True)
        layout.addWidget(self.set_shiftButton,  row, 2)
        self.set_shiftButton.setDisabled(True)
        self.set_shiftButton.clicked.connect(self.shift_spectrum)

        row += 1
        self.flux_ppmLabel = QLabel("Relative Flux")
        self.flux_ppmEdit = QLineEdit(" 1")
        self.flux_ppmEdit.setValidator(validfloat)
        self.flux_ppmEdit.editingFinished.connect(self.OnFlux_ppmEnter)
        self.flux_ppmUnit = QLabel("ppm")
        layout.addWidget(self.flux_ppmLabel,row,0)
        layout.addWidget(self.flux_ppmEdit,row,1)
        layout.addWidget(self.flux_ppmUnit,row,2)

        row += 1
        self.conversionLabel = QLabel("Conversion")
        self.conversionEdit = QLineEdit(" 25.0")
        self.conversionEdit.setValidator(validfloat)
        self.conversionEdit.editingFinished.connect(self.OnConversionEnter)
        self.conversionUnit = QLabel("e<sup>-</sup>/counts")
        layout.addWidget(self.conversionLabel,row,0)
        layout.addWidget(self.conversionEdit,row,1)
        layout.addWidget(self.conversionUnit,row,2)
        row += 1
        self.fluxLabel = QLabel("Flux")
        self.fluxEdit = QLineEdit(" 100.0")
        self.fluxEdit.setValidator(validfloat)
        self.fluxEdit.editingFinished.connect(self.OnFluxEnter)
        self.fluxUnit = QLabel("e<sup>-</sup>/s")
        layout.addWidget(self.fluxLabel,row,0)
        layout.addWidget(self.fluxEdit,row,1)
        layout.addWidget(self.fluxUnit,row,2)
        row += 1
        self.VOALabel = QLabel("Measurement")
        self.VOAEdit = QLineEdit(" 10.0")
        self.VOAEdit.setValidator(validfloat)
        self.VOAEdit.editingFinished.connect(self.OnVOAEnter)
        self.VOAUnit = QLabel("pA")
        layout.addWidget(self.VOALabel,row,0)
        layout.addWidget(self.VOAEdit,row,1)
        layout.addWidget(self.VOAUnit,row,2)
        
        
        
        return layout
        
    def set_dataset(self):
        item_text = self.mainList.currentText()
        self.parent.main = item_text.split(':')[0]
        self.updateInfo()

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
        
    def updateInfo(self):
        if '_relationship' not in self.parent.datasets:
            return
        spectrum_list = ['None']
        reference_list = ['None']
        data_list = []
        
        self.key = self.info_key = self.parent.main
        self.parent.set_dataset()
        spectrum_data = False
        info_index= 0
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
                        spectrum_data = True
                        spectrum_list.append(f'{key}: {self.parent.datasets[key].title}')
                        if self.info_key == key:
                            info_index = len(spectrum_list)-1
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
        elif self.parent.dataset.data_type.name == 'IMAGE':
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
            else:
                self.timeEdit.setText('0')
            if 'convergence_angle' in self.parent.dataset.metadata['experiment']:
                self.convEdit.setText(f"{self.parent.dataset.metadata['experiment']['convergence_angle']}")
            else:
                self.convEdit.setText('0')
            if 'collection_angle' in self.parent.dataset.metadata['experiment']:
                self.collEdit.setText(f"{self.parent.dataset.metadata['experiment']['collection_angle']}")
            else:
                self.collEdit.setText('0')
            self.E0Edit.setText(f"{self.parent.dataset.metadata['experiment']['acceleration_voltage']/1000:.0f}")
        
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
        self.set_energy_scale()

   
    def set_energy_scale(self, value=0):
        if 'SPEC' in self.parent.dataset.data_type.name:
            self.energy_scale = self.parent.datasets[self.key].get_spectral_dims(return_axis=True)[0]
            dispersion = self.parent.datasets[self.key].get_dimension_slope(self.energy_scale)
            self.energy_scale *= (float(self.dispersionEdit.displayText()) / dispersion)
            self.energy_scale += (float(self.offsetEdit.displayText()) - self.energy_scale[0])
            self.parent.plotUpdate()
        elif self.parent.dataset.data_type.name == 'IMAGE':
            pixel_size_x = float(self.dispersionEdit.displayText())
            pixel_size_y = float(self.offsetEdit.displayText())
            self.parent.dataset.x = np.arange(self.parent.dataset.shape[0]) * pixel_size_x
            self.parent.dataset.y = np.arange(self.parent.dataset.shape[1]) * pixel_size_y
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