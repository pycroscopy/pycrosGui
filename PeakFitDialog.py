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
from PyQt5 import QtWidgets

import numpy as np
import sidpy
import scipy

from pyTEMlib import eels_tools

from periodic_table import PeriodicTable

class PeakFitDialog(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(PeakFitDialog, self).__init__(parent)
    
        self.parent = parent
        layout = self.get_sidbar()
        self.setLayout(layout)    
        self.setWindowTitle("Peak Fit")
        self.peak_key = ''
        self.parent = parent
        self.dataset = parent.dataset
        
        self.model = []
        self.peaks = {}
        

    def get_sidbar(self): 
        validfloat = QtWidgets.QDoubleValidator()
        validint = QtWidgets.QIntValidator()        
        
        layout = QtWidgets.QGridLayout()
        row = 0 
        self.mainList = QtWidgets.QComboBox(self)
        self.mainList.addItem("None")
        layout.addWidget(self.mainList,  row,0, 1, 3)
        layout.setColumnStretch(0, 3)  

        self.mainList.activated[str].connect(self.update_peak_dataset)
        
        row += 1
        self.fit_areaButton = QtWidgets.QPushButton()
        self.fit_areaButton.setStyleSheet('QtWidgets.QPushButton {background-color: blue; color: white;}')
        self.fit_areaButton.setText("Fit Area")
        layout.addWidget(self.fit_areaButton,  row,0, 1, 3)
        layout.setColumnStretch(0, 3) 
        # self.fit_areaButton.clicked.connect(self.set_fit_area)
        
        row += 1
        self.fit_startLabel = QtWidgets.QLabel("Start Fit")
        self.fit_startEdit = QtWidgets.QLineEdit(" 3.0")
        # self.fit_startEdit.setValidator(validfloat)
        self.fit_startEdit.editingFinished.connect(self.on_fit_start_enter)
        self.fit_startUnit = QtWidgets.QLabel("eV")
        layout.addWidget(self.fit_startLabel,row,0)
        layout.addWidget(self.fit_startEdit,row,1)
        layout.addWidget(self.fit_startUnit,row,2)

        row += 1
        self.fit_endLabel = QtWidgets.QLabel("End Fit")
        self.fit_endEdit = QtWidgets.QLineEdit(" 30.0")
        self.fit_endEdit.setValidator(validfloat)
        self.fit_endEdit.editingFinished.connect(self.on_fit_end_enter)
        self.fit_endUnit = QtWidgets.QLabel("eV")
        layout.addWidget(self.fit_endLabel,row,0)
        layout.addWidget(self.fit_endEdit,row,1)
        layout.addWidget(self.fit_endUnit,row,2)

        row += 1
        self.find_peakButton = QtWidgets.QPushButton()
        self.find_peakButton.setStyleSheet('QtWidgets.QPushButton {background-color: blue; color: white;}')
        self.find_peakButton.setText("Peak Finding")
        layout.addWidget(self.find_peakButton,  row,0, 1, 3)
        layout.setColumnStretch(0, 3) 
        self.find_peakButton.clicked.connect(self.smooth)
       

        row += 1
        self.addZL_Button = QtWidgets.QPushButton()
        self.addZL_Button.setText("use zero loss")
        self.addZL_Button.setCheckable(True)
        layout.addWidget(self.addZL_Button,  row, 0)
        # self.conv_LL_Button.clicked.connect(self.update_ll_plot)

        self.addLL_Button = QtWidgets.QPushButton()
        self.addLL_Button.setText("use low loss")
        self.addLL_Button.setCheckable(True)
        layout.addWidget(self.addLL_Button,  row, 1)
        
        self.addCL_Button = QtWidgets.QPushButton()
        self.addCL_Button.setText("use core loss")
        self.addCL_Button.setCheckable(True)
        layout.addWidget(self.addCL_Button,  row, 2)
        
        row +=1
        self.smoothLabel = QtWidgets.QLabel("Iterations")
        layout.addWidget(self.smoothLabel,  row, 0)
        self.smmoothList = QtWidgets.QComboBox(self)
        self.smmoothList.addItems(["0", "1", "2", "3"])
        layout.addWidget(self.smmoothList,  row, 1)

        self.smoothButton = QtWidgets.QPushButton()
        self.smoothButton.setText("Smooth")
        self.smoothButton.setCheckable(True)
        layout.addWidget(self.smoothButton,  row, 2)
        layout.addWidget(self.smoothButton,  row, 2)
        self.smoothButton.clicked.connect(self.smooth)

        row += 1
        self.find_PeakLabel = QtWidgets.QLabel("Number")
        self.find_PeakEdit = QtWidgets.QLineEdit(" 0")
        self.find_PeakEdit.setValidator(validint)
        #self.find_PeakEdit.editingFinished.connect(self.find_elements)
        self.find_PeakButton = QtWidgets.QPushButton()
        self.find_PeakButton.setText("Find")
        self.find_PeakEdit.editingFinished.connect(self.find_peaks)
       
        layout.addWidget(self.find_PeakLabel,row,0)
        layout.addWidget(self.find_PeakEdit,row,1)
        layout.addWidget(self.find_PeakButton,row,2)

        row += 1
        self.peaksButton = QtWidgets.QPushButton()
        self.peaksButton.setStyleSheet('QtWidgets.QPushButton {background-color: blue; color: white;}')
        self.peaksButton.setText("Peaks")
        layout.addWidget(self.peaksButton,  row,0, 1, 3)
        layout.setColumnStretch(0, 3) 
        self.peaksButton.clicked.connect(self.fit_peaks)
       
        row +=1
        self.peaksLabel = QtWidgets.QLabel("Peak:")
        self.peakList = QtWidgets.QComboBox(self)
        self.peakList.addItem("Peak 1")
        self.peakList.addItem("add Peak") 
        self.peaksOut = QtWidgets.QLabel(" ")
        layout.addWidget(self.peakList,  row, 1)
        layout.addWidget(self.peaksLabel,  row, 0)
        layout.addWidget(self.peaksOut,  row, 2)
        self.peakList.activated[str].connect(self.update)

        #row +=1
        #self.symmetryLabel = QtWidgets.QLabel("Symmetry")
        #self.symmetryList = QtWidgets.QComboBox(self)
        #self.symmetry_options= 'Gauss', 'Lorentzian', 'Drude', 'Zero-Loss']
        #self.symmetryList.addItems(self.symmetry_options) 
        #layout.addWidget(self.symmetryList,  row, 1)
        
        
        row +=1
        self.peak_positionLabel = QtWidgets.QLabel("Position")
        self.peak_positionEdit = QtWidgets.QLineEdit(" 5.0")
        self.peak_positionEdit.setValidator(validfloat)
        self.peak_positionEdit.editingFinished.connect(self.on_position_enter)
        self.peak_positionUnit = QtWidgets.QLabel("eV")
        layout.addWidget(self.peak_positionLabel,row,0)
        layout.addWidget(self.peak_positionEdit,row,1)
        layout.addWidget(self.peak_positionUnit,row,2)

        row += 1
        self.peak_amplitudeLabel = QtWidgets.QLabel("Amplitude:")
        self.peak_amplitudeEdit = QtWidgets.QLineEdit(" 5.0")
        self.peak_amplitudeEdit.setValidator(validfloat)
        self.peak_amplitudeEdit.editingFinished.connect(self.on_amplitude_enter)
        self.peak_amplitudeUnit = QtWidgets.QLabel("eV")
        layout.addWidget(self.peak_amplitudeLabel,row,0)
        layout.addWidget(self.peak_amplitudeEdit,row,1)
        layout.addWidget(self.peak_amplitudeUnit,row,2)

        row += 1
        self.peak_widthLabel = QtWidgets.QLabel("Width FWHM")
        self.peak_widthEdit = QtWidgets.QLineEdit(" 5.0")
        self.peak_widthEdit.setValidator(validfloat)
        self.peak_widthEdit.editingFinished.connect(self.on_width_enter)
        self.peak_widthUnit = QtWidgets.QLabel("eV")
        layout.addWidget(self.peak_widthLabel,row,0)
        layout.addWidget(self.peak_widthEdit,row,1)
        layout.addWidget(self.peak_widthUnit,row,2)

        row += 1
        self.peak_asymmetryLabel = QtWidgets.QLabel("Asymmetry")
        self.peak_asymmetryEdit = QtWidgets.QLineEdit(" 5.0")
        self.peak_asymmetryEdit.setValidator(validfloat)
        self.peak_asymmetryEdit.editingFinished.connect(self.on_multiplier_enter)
        self.peak_asymmetryUnit = QtWidgets.QLabel("a.u.")
        layout.addWidget(self.peak_asymmetryLabel,row,0)
        layout.addWidget(self.peak_asymmetryEdit,row,1)
        layout.addWidget(self.peak_asymmetryUnit,row,2)

        row += 1
        self.white_lineButton = QtWidgets.QPushButton()
        self.white_lineButton.setStyleSheet('QtWidgets.QPushButton {background-color: blue; color: white;}')
        self.white_lineButton.setText("White Lines")
        layout.addWidget(self.white_lineButton,  row,0, 1, 3)
        layout.setColumnStretch(0, 3)       
        self.white_lineButton.clicked.connect(self.get_white_lines)
         
        
        row += 1
        self.ratioLabel = QtWidgets.QLabel("Ratio:")
        self.ratioList = QtWidgets.QComboBox(self)
        self.ratioList.addItem("None")
        self.ratioOut = QtWidgets.QLabel("")
        layout.addWidget(self.ratioOut,  row, 2)
        layout.addWidget(self.ratioList,  row, 1)
        layout.addWidget(self.ratioLabel,  row, 0)# self.conv_LL_Button.clicked.connect(self.update_ll_plot)
        self.ratioList.activated[str].connect(self.update_white_line_ratio)

        row += 1
        self.sumLabel = QtWidgets.QLabel("Sum:")
        self.sumList = QtWidgets.QComboBox(self)
        self.sumList.addItem("None")
        self.sumOut = QtWidgets.QLabel("")
        layout.addWidget(self.sumOut,  row, 2)
        layout.addWidget(self.sumList,  row, 1)
        layout.addWidget(self.sumLabel,  row, 0)
        self.sumList.activated[str].connect(self.update_white_line_sum)
        
        return layout
        
    def update_peak_sidebar(self):
        if '_relationship' not in self.parent.datasets:
            return
        spectrum_list = ['None']
        peak_index = 0
        if 'find_peak' in self.parent.datasets['_relationship']:
            self.peak_key = self.parent.datasets['_relationship']['find_peak']
        else:
            self.peak_key = 'None'

        for index, key in enumerate(self.parent.datasets.keys()):
            if isinstance(self.parent.datasets[key], sidpy.Dataset):
                if 'SPECTR' in self.parent.datasets[key].data_type.name:
                    spectrum_list.append(f'{key}: {self.parent.datasets[key].title}')
                if key == self.peak_key:
                    peak_index = index + 1

        if peak_index >len(spectrum_list) - 1:
            peak_index = len(spectrum_list) - 1
        self.mainList.clear()
        for item in spectrum_list:
            self.mainList.addItem(item)
        self.mainList.setCurrentIndex(peak_index)
        
        if 'peak_fit' not in self.parent.dataset.metadata:
            energy_scale = self.parent.dataset.get_spectral_dims(return_axis=True)[0].values
            self.parent.dataset.metadata['peak_fit'] = {'fit_start': energy_scale[10], 
                                                     'fit_end': energy_scale[-10]}
            

        self.fit_startEdit.setText(f"{self.parent.dataset.metadata['peak_fit']['fit_start']:.3f}")
        self.fit_endEdit.setText(f"{self.parent.dataset.metadata['peak_fit']['fit_end']:.3f}")
        self.update_peak_dataset()
        
    def update_peak_dataset(self, value=0):
        
        self.peak_key = self.mainList.currentText().split(':')[0]
        if 'None' in self.peak_key:
            return
        if self.peak_key not in self.parent.datasets.keys():
            return
        self.parent.peak_key = self.peak_key
        self.parent.datasets['_relationship']['find_peak'] = self.peak_key
        
        self.parent.main = self.peak_key
        self.parent.set_dataset()
        self.dataset = self.parent.datasets[self.peak_key]

        if 'peak_fit' not in self.dataset.metadata:
            self.dataset.metadata['peak_fit'] = {'fit_start': 0.0, 'fit_end': 0.0}
        self.peaks = self.dataset.metadata['peak_fit']

        self.update()    
        
    def update_peak_plot(self):
        # self.set_additional_spectra()
        self.parent.plotUpdate()

    
    def get_spectrum(self, key=None):
        if key is None:
            dataset = self.parent.dataset 
        elif key in self.parent.datasets:
            dataset = self.parent.datasets[key]
        else:
            return

        if dataset.data_type.name == 'SPECTRUM':
            self.parent.x = 0
            self.parent.y = 0
            spectrum = dataset
        else:
            spectrum = dataset[self.parent.x, self.parent.y]
        spectrum.data_type ='SPECTRUM'
        return spectrum

    def set_peak_list(self):
        if 'peaks' not in self.peaks:
            self.peaks['peaks'] = {}
        for key in self.peaks['peaks']:
            if key.isdigit():
                self.peakList.addItem(f'Peak {int(key) + 1}')
        self.peakList.addItem('add Peak')

    def update(self, index=0):
        
        self.dataset = self.parent.dataset
        energy_scale = self.dataset.get_spectral_dims(return_axis=True)[0].values
        if 'peaks' not in self.peaks:
            self.peaks['peaks'] = {}
        if 'fit_start' not in self.peaks:
            self.peaks['fit_start'] = energy_scale[10]
            self.peaks['fit_end'] = energy_scale[-10]
        self.fit_startEdit.setText(f"{self.peaks['fit_start']:.2f}")
        self.fit_endEdit.setText(f"{self.peaks['fit_end']:.2f}")

        item = self.peakList.currentText()
        peak_index = self.peakList.currentIndex()
        
        if str(peak_index) not in self.peaks['peaks']:
            self.peaks['peaks'][str(peak_index)] = {'position': energy_scale[10], 'amplitude': 1000.0,
                                                    'width': 1.0, 'type': 'Gauss', 'asymmetry': 0}
            if 'peak_fit' in self.parent.dataset.metadata:
                peak_list = self.get_input()
                self.parent.dataset.metadata['peak_fit']['peak_out_list'] = np.reshape(peak_list, [len(peak_list) // 3, 3]) 
        # self.sidebar[8, 0].value = self.peaks['peaks'][str(peak_index)]['type']

        if 'associated_edge' in self.peaks['peaks'][str(peak_index)]:
           self.peaksOut.setText(self.peaks['peaks'][str(peak_index)]['associated_edge'])
        else:
           self.peaksOut.setText(" ")
        self.peak_positionEdit.setText(f"{self.peaks['peaks'][str(peak_index)]['position']}")
        self.peak_amplitudeEdit.setText(f"{self.peaks['peaks'][str(peak_index)]['amplitude']}") 
        self.peak_widthEdit.setText(f"{self.peaks['peaks'][str(peak_index)]['width']}")
        if 'asymmetry' not in self.peaks['peaks'][str(peak_index)]:
            self.peaks['peaks'][str(peak_index)]['asymmetry'] = 0.
        self.peak_asymmetryEdit.setText(f"{self.peaks['peaks'][str(peak_index)]['asymmetry']}") 
        
        self.peakList.clear()
        for key in self.peaks['peaks']:
            if key.isdigit():
                self.peakList.addItem(f'Peak {int(key)+1}')
        self.peakList.setCurrentIndex(peak_index)
        self.peakList.addItem('add Peak')



    def get_white_lines(self):
        self.ratioList.clear()
        self.sumList.clear()
        if 'core_loss' in self.parent.dataset.metadata:
            if 'peak_fit' in self.parent.dataset.metadata:
                
                self.white_lines = self.find_white_lines()
                for key in self.white_lines['ratio']:
                    self.ratioList.addItem(key)
                self.ratioList.setCurrentIndex(0)
                for key in self.white_lines['sum']:
                    self.sumList.addItem(key)
                self.sumList.setCurrentIndex(0)
                self.update_white_line_ratio()
                self.update_white_line_sum()


    def update_white_line_ratio(self, value=0):
        key = self.ratioList.currentText()
        if key not in self.white_lines['ratio']:
            return
        self.ratioOut.setText(f"{self.white_lines['ratio'][key]*100:.2f}%")  
        
    def update_white_line_sum(self, value=0):
        key = self.sumList.currentText()
        if key not in self.white_lines['sum']:
            return
        self.sumOut.setText(f"{self.white_lines['sum'][key]*100:.2f}%")

    def set_dataset(self):
        
        item_text = self.mainList.currentText()
        if item_text == 'None':
            return
        self.parent.main = item_text.split(':')[0]
        self.peak_key = self.parent.main

        self.parent.dataset = self.parent.datasets[self.parent.main]
        self.dataset = self.parent.dataset
        energy_scale = self.dataset.get_spectral_dims(return_axis=True)[0].values
        self.parent.datasets['_relationship']['peak_fit'] = self.peak_key
        self.parent.InfoDialog.updateInfo()
        if 'peak_fit' not in self.dataset.metadata:
            self.dataset.metadata['peak_fit'] = {}
            if 'core_loss' in self.dataset.metadata:
                if 'fit_area' in self.dataset.metadata['core_loss']:
                    self.dataset.metadata['peak_fit']['fit_start'] = self.dataset.metadata['edges']['fit_area']['fit_start']
                    self.dataset.metadata['peak_fit']['fit_end'] = self.dataset.metadata['edges']['fit_area']['fit_end']
                self.dataset.metadata['peak_fit']['peaks'] = {'0': {'position': energy_scale[1],
                                                                    'amplitude': 1000.0, 'width': 1.0,
                                                                    'type': 'Gauss', 'asymmetry': 0}}
        self.peaks = self.dataset.metadata['peak_fit']
        if 'fit_start' not in self.peaks:
            self.peaks['fit_start'] = energy_scale[1]
        if 'fit_end' not in self.peaks:
            self.peaks['fit_end'] = energy_scale[-2]

        if 'peak_model' in self.peaks:
            self.peak_model = self.peaks['peak_model']
            self.model = self.peak_model
            if 'edge_model' in self.peaks:
                self.model = self.model + self.peaks['edge_model']
        else:
            self.model = np.array([])
            self.peak_model = np.array([])
        if 'peak_out_list' in self.peaks:
            self.peak_out_list = self.peaks['peak_out_list']
        self.set_peak_list()

        # check whether a core loss analysis has been done previously
        if not hasattr(self, 'core_loss') and 'edges' in self.dataset.metadata:
            self.core_loss = True
        else:
            self.core_loss = False

        self.update()
                           
    
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

    def get_spectrum(self, key=None):
        if key is None:
            dataset = self.parent.dataset 
        elif key in self.parent.datasets:
            dataset = self.parent.datasets[key]
        else:
            return

        if dataset.data_type.name == 'SPECTRUM':
            self.parent.x = 0
            self.parent.y = 0
            spectrum = dataset
        else:
            spectrum = dataset[self.parent.x, self.parent.y]
    
        return spectrum


    def get_additional_spectra(self):        
        spectrum = self.get_spectrum()
        energy_scale = spectrum.get_spectral_dims(return_axis=True)[0].values
        x = self.parent.x
        y = self.parent.y
        additional_spectra = {}
        if 'peak_fit' in self.parent.dataset.metadata:
            if 'peak_model' in self.parent.dataset.metadata['peak_fit']:
                additional_spectra['start model'] = self.parent.dataset.metadata['peak_fit']['start_model']
                additional_spectra['peak_fit model'] = self.dataset.metadata['peak_fit']['peak_model']
                additional_spectra['full model'] = additional_spectra['start model'] + additional_spectra['peak_fit model']  
                additional_spectra['difference'] = np.array(spectrum) - additional_spectra['full model']
                p =[]
                if 'parameter' in self.parent.dataset.metadata['peak_fit']:
                    p = self.parent.dataset.metadata['peak_fit']['parameter'][x, y]
                else:
                    p = self.parent.dataset.metadata['peak_fit']['peak_out_list']
                for index in range(len(p)): 
                    additional_spectra[f'peak {index}']= gauss(energy_scale, p[index])
        return additional_spectra

    def get_input(self):
        p_in = []
        for key, peak in self.peaks['peaks'].items():
            if key.isdigit():
                p_in.append(peak['position'])
                p_in.append(peak['amplitude'])
                p_in.append(peak['width'])
        return p_in
    
    def get_model(self):
        energy_scale = self.parent.dataset.get_spectral_dims(return_axis=True)[0].values
        self.energy_scale = energy_scale.copy()
        x = self.parent.x
        y = self.parent.y
        
        model = np.zeros(len(energy_scale))
        if self.addCL_Button.isChecked():
            if 'core_loss' in self.parent.dataset.metadata:
                p = self.parent.dataset.metadata['core_loss']['parameter'][x, y]
                xsec = self.parent.dataset.metadata['core_loss']['xsections']
                number_of_edges = xsec.shape[0]
                self.parent.dataset.metadata['core_loss']['parameter'][x, y] = p                             
                model = eels_tools.core_loss_model(energy_scale, p, number_of_edges, xsec)
        if self.addZL_Button.isChecked():
            if 'zero_loss' in self.parent.dataset.metadata:
                parameter = self.parent.dataset.metadata['zero_loss']['parameter'][x, y]
                model  = eels_tools.zero_loss_function(energy_scale, parameter)
        if self.addLL_Button.isChecked():
            if 'low_loss' in self.parent.dataset.metadata:
                parameter = list(self.parent.dataset.metadata['plasmon']['parameter'][x, y])
                model = eels_tools.multiple_scattering(energy_scale, parameter)#  * anglog
        return np.array(model)     

    def find_peaks(self, value=0):
        number_of_peaks = int(self.find_PeakEdit.displayText())
        if number_of_peaks > len(self.parent.dataset.metadata['peak_fit']['peak_gmm_list']):
            number_of_peaks = len(self.parent.dataset.metadata['peak_fit']['peak_gmm_list'])
        spectrum = self.get_spectrum()
        # noise without zero-loss peak difference which is rather large usually
        noise_level = np.std((spectrum-self.model)[300:]) * 2
        self.peak_list = []
        self.peaks['peaks'] = {}
        #self.selected_peak_out_list = self.peak_out_list[:number_of_peaks]  
        new_number_of_peaks = 0
        self.parent.dataset.metadata['peak_fit']['peak_out_list'] = []   
        for i in range(number_of_peaks):
            p = self.parent.dataset.metadata['peak_fit']['peak_gmm_list'][i]
            
            if abs(p[1])>noise_level:
                self.parent.dataset.metadata['peak_fit']['peak_out_list'].append(p) 
                self.peaks['peaks'][str(new_number_of_peaks)] = {'position': p[0], 'amplitude': p[1], 'width': p[2], 'type': 'Gauss',
                                        'asymmetry': 0}
                new_number_of_peaks += 1
        self.find_PeakEdit.setText(str(new_number_of_peaks))
        
        self.peakList.setCurrentIndex(0)
        self.parent.plotUpdate()
        self.update()

    def fit_peaks(self, value=0):
        """Fit spectrum with peaks given in peaks dictionary"""

        self.dataset = self.parent.dataset
        spectrum = self.get_spectrum()
        self.model = self.get_model()
        full_energy_scale = spectrum.get_spectral_dims(return_axis=True)[0].values
        start_channel = np.searchsorted(full_energy_scale, self.peaks['fit_start'])
        end_channel = np.searchsorted(full_energy_scale, self.peaks['fit_end'])
       
        energy_scale = full_energy_scale[start_channel:end_channel]
        # select the core loss model if it exists. Otherwise, we will fit to the full spectrum.
        x = self.parent.x
        y = self.parent.y
        
        # if we have a core loss model we will only fit the difference between the model and the data.
        difference = np.array(spectrum[start_channel:end_channel] - self.model[start_channel:end_channel])
        p_in = self.get_input()
        # find the optimum fitting parameters
        
        [self.p_out, _] = scipy.optimize.leastsq(eels_tools.residuals3, np.array(p_in, dtype=np.float64),
                                                    args=(energy_scale, difference)  ) # , False))
        # construct the fit data from the optimized parameters
        self.peak_model = eels_tools.gmm(full_energy_scale, self.p_out)  # , False)
         
        if 'peak_fit' not in self.dataset.metadata:
            self.dataset.metadata['peak_fit'] = {}
        if 'parameter' not in self.dataset.metadata['peak_fit']:
            if self.dataset.data_type.name == 'SPECTRUM':
                self.dataset.metadata['peak_fit']['parameter'] = np.zeros([1,1, len(self.p_out)])
            else:
                self.dataset.metadata['peak_fit']['parameter'] = np.zeros([self.dataset.shape[0], self.dataset.shape[1], len(self.p_out)])  
        self.dataset.metadata['peak_fit'] = {'fit_start': self.peaks['fit_start'], 
                                             'fit_end': self.peaks['fit_end']}
        
        for key, peak in self.peaks['peaks'].items():
            if key.isdigit():
                p_index = int(key)*3
                self.peaks['peaks'][key] = {'position': self.p_out[p_index],
                                            'amplitude': self.p_out[p_index+1],
                                            'width': self.p_out[p_index+2],
                                            'type': 'Gauss',
                                            'associated_edge': ''}

        

        self.dataset.metadata['peak_fit']['start_model'] = self.model
        self.model = self.model + self.peak_model
        self.dataset.metadata['peak_fit']['peak_model'] = self.peak_model
        self.dataset.metadata['peak_fit']['peak_out_list']  = np.reshape(self.p_out, [len(self.p_out) // 3, 3])
        self.dataset.metadata['peak_fit']['peaks'] = self.peaks.copy()
        
        self.parent.dataset.metadata['plot']['additional_spectra'] = 'PeakFit'
        eels_tools.find_associated_edges(self.parent.dataset)
        """if 'core_loss' in self.parent.dataset.metadata:
            for key, edge in self.parent.dataset.metadata['core_loss']['edges'].items():
                if 'associated_peaks'in edge:
                    for key, peak in edge['associated_peaks'].items():
                        self.peaks[int(key)]['associated_edge'] = peak
        """
        # Find and calculate white line ratios after fitting peaks
        
        self.update()

        self.update_peak_plot()
        self.parent.status.showMessage('Fitting peaks -- success')

    def find_white_lines(self):
        return eels_tools.find_white_lines(self.parent.dataset)

    def smooth(self, value=0):
        """Fit lots of Gaussian to spectrum and let the program sort it out

        We sort the peaks by area under the Gaussians, assuming that small areas mean noise.

        """
        spectrum = self.parent.get_spectrum_dataset()

        iterations = 1  # ToDo: self.smmoothList.currentIndex()
        self.find_PeakEdit.setText('0')
        self.parent.status.showMessage('Fitting Gaussian Mixing Model' )
        
        self.model = self.get_model()

        self.peak_model, self.peak_out_list, number_of_peaks = smooth(spectrum-self.model, iterations, False)
        self.parent.dataset.metadata['peak_fit']['start_model'] = self.model
        self.model = self.model + self.peak_model
        self.parent.dataset.metadata['peak_fit']['peak_model'] = self.peak_model
        self.parent.dataset.metadata['peak_fit']['peak_out_list'] = self.peak_out_list
        self.parent.dataset.metadata['peak_fit']['peak_gmm_list'] = self.peak_out_list
        
        peaks, prop = scipy.signal.find_peaks(self.peak_model, width=3)

        self.find_PeakEdit.setText(f"{len(peaks)}")
        
        self.update()
        self.parent.dataset.metadata['plot']['additional_spectra'] = 'PeakFit'
        
        self.update_peak_plot()
        self.smoothButton.setChecked(False)
        self.parent.status.showMessage('Fitting Gaussian Mixing Model -- success ' )

    def on_fit_start_enter(self):
        self.peaks['fit_start'] = float(self.fit_startEdit.displayText())

    def on_fit_end_enter(self):
        self.peaks['fit_end'] = float(self.fit_endEdit.displayText())
    
    def on_position_enter(self):
        index = self.peakList.currentIndex()
        peak = self.peaks['peaks'][str(self.peakList.currentIndex())]
        peak['position'] = float(self.peak_positionEdit.displayText())  
        self.parent.dataset.metadata['peak_fit']['peak_out_list'][index][0] = float(self.peak_widthEdit.displayText())  
        self.update_peak_plot()

    def on_amplitude_enter(self):
        index = self.peakList.currentIndex()
        self.peaks['peaks'][str(self.peakList.currentIndex())]['amplitude'] = float(self.peak_amplitudeEdit.displayText())  
        self.parent.dataset.metadata['peak_fit']['peak_out_list'][index][1] = float(self.peak_widthEdit.displayText())  
        self.update_peak_plot()

    def on_width_enter(self):
        index = self.peakList.currentIndex()
        self.peaks['peaks'][str(index)]['width'] = float(self.peak_widthEdit.displayText())  
        self.parent.dataset.metadata['peak_fit']['peak_out_list'][index][2] = float(self.peak_widthEdit.displayText())  
        self.update_peak_plot()

    def on_multiplier_enter(self):
        edge = self.edges[str(self.edgeList.currentIndex())] * self.parent.intensity_scale
        
        edge['areal_density'] = float(self.edge_multiplierEdit.displayText())  
        if 'core_loss' in self.parent.dataset.metadata:
            if self.dataset.data_type.name == 'SPECTRUM':
                self.parent.x = 0
                self.parent.y = 0
            self.parent.dataset.metadata['core_loss']['parameter'][self.parent.x, self.parent.y][self.edgeList.currentIndex()+5] = float(self.edge_multiplierEdit.displayText())
        self.update_cl_plot()            

def smooth(dataset, iterations, advanced_present):
    """Gaussian mixture model (non-Bayesian)

    Fit lots of Gaussian to spectrum and let the program sort it out
    We sort the peaks by area under the Gaussians, assuming that small areas mean noise.

    """

    # TODO: add sensitivity to dialog and the two functions below
    #peaks = dataset.metadata['peak_fit']
    
    #peak_model, peak_out_list = eels_tools.find_peaks(dataset, peaks['fit_start'], peaks['fit_end'])
    peak_model, peak_out_list = eels_tools.gaussian_mixture_model(dataset, p_in=None)

    new_list = np.reshape(peak_out_list, [len(peak_out_list) // 3, 3])
    area = np.sqrt(2 * np.pi) * np.abs(new_list[:, 1]) * np.abs(new_list[:, 2] / np.sqrt(2 * np.log(2)))
    arg_list = np.argsort(area)[::-1]
    area = area[arg_list]
    peak_out_list = new_list[arg_list]

    number_of_peaks = np.searchsorted(area * -1, -np.average(area))

    return peak_model, peak_out_list, number_of_peaks


def gauss(x, p):  # p[0]==mean, p[1]= amplitude p[2]==fwhm,
    """Gaussian Function

        p[0]==mean, p[1]= amplitude p[2]==fwhm
        area = np.sqrt(2* np.pi)* p[1] * np.abs(p[2] / 2.3548)
        FWHM = 2 * np.sqrt(2 np.log(2)) * sigma = 2.3548 * sigma
        sigma = FWHM/3548
    """
    if p[2] == 0:
        return x * 0.
    else:
        return p[1] * np.exp(-(x - p[0]) ** 2 / (2.0 * (p[2] / 2.3548) ** 2))
           

