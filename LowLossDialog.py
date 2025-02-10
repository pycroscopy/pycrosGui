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

class LowLossDialog(QWidget):
    def __init__(self, parent=None):
        super(LowLossDialog, self).__init__(parent)
    
        self.parent = parent
        layout = self.get_sidbar()
        self.setLayout(layout)    
        self.setWindowTitle("LowLoss")
        self.ll_key = ''

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
        self.resolutionButton = QPushButton()
        self.resolutionButton.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.resolutionButton.setText("Resolution Function")
        layout.addWidget(self.resolutionButton,  row,0, 1, 3)
        layout.setColumnStretch(0, 3) 
        self.resolutionButton.clicked.connect(self.get_resolution_function)
        
        row += 1
        self.fit_widthLabel = QLabel("fit width")
        self.fit_widthEdit = QLineEdit(" 1.0")
        self.fit_widthEdit.setValidator(validfloat)
        self.fit_widthEdit.editingFinished.connect(self.set_fit_width)
        self.fit_widthUnit = QLabel("eV")
        layout.addWidget(self.fit_widthLabel,row,0)
        layout.addWidget(self.fit_widthEdit,row, 1)
        layout.addWidget(self.fit_widthUnit,row, 2)
        
        row += 1
        self.plot_zlButton = QPushButton()
        self.plot_zlButton.setText("Plot Res.Fct.")
        self.plot_zlButton.setCheckable(True)
        layout.addWidget(self.plot_zlButton,  row, 0)
        self.plot_zlButton.clicked.connect(self.update_ll_plot)

        self.probabilityButton = QPushButton()
        self.probabilityButton.setText("Probability")
        self.probabilityButton.setCheckable(True)
        layout.addWidget(self.probabilityButton,  row, 2)
        
        row += 1
        self.drudeButton = QPushButton()
        self.drudeButton.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.drudeButton.setText("Drude")
        layout.addWidget(self.drudeButton,  row,0, 1, 3)
        layout.setColumnStretch(0, 3)        
        self.drudeButton.clicked.connect(self.get_drude)
                
        row += 1
        self.drude_startLabel = QLabel("Start Fit")
        self.drude_startEdit = QLineEdit(" 3.0")
        self.drude_startEdit.setValidator(validfloat)
        #self.drude_startEdit.editingFinished.connect(self.on_drude_start_enter)
        self.drude_startUnit = QLabel("eV")
        layout.addWidget(self.drude_startLabel,row,0)
        layout.addWidget(self.drude_startEdit,row,1)
        layout.addWidget(self.drude_startUnit,row,2)

        row += 1
        self.drude_endLabel = QLabel("End Fit")
        self.drude_endEdit = QLineEdit(" 30.0")
        self.drude_endEdit.setValidator(validfloat)
        #self.drude_endEdit.editingFinished.connect(self.OnConvEnter)
        self.drude_endUnit = QLabel("eV")
        layout.addWidget(self.drude_endLabel,row,0)
        layout.addWidget(self.drude_endEdit,row,1)
        layout.addWidget(self.drude_endUnit,row,2)

        row += 1
        self.drude_energyLabel = QLabel("Energy")
        self.drude_energyEdit = QLineEdit(" 20.0")
        self.drude_energyEdit.setValidator(validfloat)
        self.drude_energyEdit.editingFinished.connect(self.on_drude_energy_enter)
        self.drude_energyUnit = QLabel("eV")
        layout.addWidget(self.drude_energyLabel,row,0)
        layout.addWidget(self.drude_energyEdit,row,1)
        layout.addWidget(self.drude_energyUnit,row,2)

        row += 1
        self.drude_widthLabel = QLabel("Width")
        self.drude_widthEdit = QLineEdit(" 5.0")
        self.drude_widthEdit.setValidator(validfloat)
        self.drude_widthEdit.editingFinished.connect(self.on_drude_width_enter)
        self.drude_widthUnit = QLabel("eV")
        layout.addWidget(self.drude_widthLabel,row,0)
        layout.addWidget(self.drude_widthEdit,row,1)
        layout.addWidget(self.drude_widthUnit,row,2)

        row += 1
        self.drude_amplitudeLabel = QLabel("Amplitude")
        self.drude_amplitudeEdit = QLineEdit(" 3000.0")
        self.drude_amplitudeEdit.setValidator(validfloat)
        self.drude_amplitudeEdit.editingFinished.connect(self.on_drude_amplitude_enter)
        self.drude_amplitudeUnit = QLabel("eV")
        layout.addWidget(self.drude_amplitudeLabel,row,0)
        layout.addWidget(self.drude_amplitudeEdit,row,1)
        layout.addWidget(self.drude_amplitudeUnit,row,2)

        row += 1
        self.plot_drudeButton = QPushButton()
        self.plot_drudeButton.setText("Plot Drude")
        self.plot_drudeButton.setCheckable(True)
        layout.addWidget(self.plot_drudeButton,  row, 0)
        self.plot_drudeButton.clicked.connect(self.update_ll_plot)

        self.plot_dielectricButton = QPushButton()
        self.plot_dielectricButton.setText("Plot Diel Funct.")
        self.plot_dielectricButton.setCheckable(True)
        layout.addWidget(self.plot_dielectricButton,  row, 1)

        self.do_allButton = QPushButton()
        self.do_allButton.setText("Do All")
        self.do_allButton.setCheckable(True)
        layout.addWidget(self.do_allButton,  row, 2)
        
        row += 1
        self.multipleButton = QPushButton()
        self.multipleButton.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.multipleButton.setText("Multiple Scattering")
        layout.addWidget(self.multipleButton,  row,0, 1, 3)
        layout.setColumnStretch(0, 3)       
        self.multipleButton.clicked.connect(self.get_multiple_scattering)
         
        row += 1
        self.multi_startLabel = QLabel("Start Fit")
        self.multi_startEdit = QLineEdit(" 1.0")
        self.multi_startEdit.setValidator(validfloat)
        # self.multi_startEdit.editingFinished.connect(self.on_drude_amplitude_enter)
        self.multi_startUnit = QLabel("eV")
        layout.addWidget(self.multi_startLabel,row,0)
        layout.addWidget(self.multi_startEdit,row,1)
        layout.addWidget(self.multi_startUnit,row,2)

        row += 1
        self.multi_endLabel = QLabel("End Fit")
        self.multi_endEdit = QLineEdit("-1")
        self.multi_endEdit.setValidator(validfloat)
        # self.multi_endEdit.editingFinished.connect(self.OnConvEnter)
        self.multi_endUnit = QLabel("eV")
        layout.addWidget(self.multi_endLabel,row,0)
        layout.addWidget(self.multi_endEdit,row,1)
        layout.addWidget(self.multi_endUnit,row,2)

        row += 1
        self.multi_thicknessLabel = QLabel("Thickness")
        self.multi_thicknessEdit = QLineEdit(" 100.0")
        self.multi_thicknessEdit.setValidator(validfloat)
        self.multi_thicknessEdit.editingFinished.connect(self.on_multi_thickness_enter)
        self.multi_thicknessUnit = QLabel("iMFP")
        layout.addWidget(self.multi_thicknessLabel,row,0)
        layout.addWidget(self.multi_thicknessEdit,row,1)
        layout.addWidget(self.multi_thicknessUnit,row,2)
        
        row += 1
        self.plot_multiButton = QPushButton()
        self.plot_multiButton.setText("Plot Low Loss Model")
        self.plot_multiButton.setCheckable(True)
        layout.addWidget(self.plot_multiButton,  row, 0)
        self.plot_multiButton.clicked.connect(self.update_ll_plot)
        return layout
        
    def update_ll_sidebar(self):
        if '_relationship' not in self.parent.datasets:
            return
        spectrum_list = ['None']
        ll_index = 0

        if 'low_loss' in self.parent.datasets['_relationship']:
            self.ll_key = self.parent.datasets['_relationship']['low_loss']
        else:
            self.ll_key = 'None' 
        for index, key in enumerate(self.parent.datasets.keys()):
            if isinstance(self.parent.datasets[key], sidpy.Dataset):
                if 'SPECTR' in self.parent.datasets[key].data_type.name:
                    energy_offset = self.parent.datasets[key].get_spectral_dims(return_axis=True)[0][0]
                    if energy_offset < 0:
                        spectrum_list.append(f'{key}: {self.parent.datasets[key].title}')
                if key == self.ll_key:
                    ll_index = index + 1

        if ll_index >len(spectrum_list) - 1:
            ll_index = len(spectrum_list) - 1
        self.mainList.clear()
        for item in spectrum_list:
            self.mainList.addItem(item)
        self.mainList.setCurrentIndex(ll_index)
        
        self.drude_startEdit.setText(f"{float(self.drude_startEdit.displayText()):.3f}")
        self.update_ll_dataset()
        
    def update_ll_dataset(self, value=0):
        self.ll_key = self.mainList.currentText().split(':')[0]
        if self.ll_key not in self.parent.datasets.keys():
            return
        self.parent.lowloss_key = self.ll_key
        if 'None' in self.ll_key:
            return
        self.parent.main = self.ll_key
        self.dataset = self.parent.datasets[self.ll_key]
        if float(self.multi_endEdit.displayText())< 0:
            energy_scale = self.dataset.get_spectral_dims(return_axis=True)[0]
            self.multi_endEdit.setText(f"{energy_scale[-2]:.3f}")

        self.parent.set_dataset()
        self.parent.plotUpdate()
        
    def update_ll_plot(self):
        # self.set_additional_spectra()
        self.parent.plotUpdate()

    def get_additional_spectra(self):        
        spectrum = self.parent.get_spectrum_dataset()
        energy_scale = spectrum.get_spectral_dims(return_axis=True)[0].values
        x = self.parent.x
        y = self.parent.y

        add_difference = False
        additional_spectra = {}
        ## We will add difference spectrum last
        
        additional_spectra['difference'] = np.array(spectrum)
        if self.plot_drudeButton.isChecked():
            if 'plasmon' in self.parent.dataset.metadata:
                parameter = list(self.parent.dataset.metadata['plasmon']['parameter'][x, y])
                plasmon = eels_tools.energy_loss_function(energy_scale, parameter)   
                start_plasmon = np.searchsorted(energy_scale, 0)+1
                plasmon[:start_plasmon] = 0.
                additional_spectra['plasmon'] = plasmon
                additional_spectra['difference'] -= np.array(plasmon)
        
        if self.plot_multiButton.isChecked():
            if 'plasmon' in self.parent.dataset.metadata:
                if 'low_loss_model' not in self.parent.add_spectrum:
                    self.parent.add_spectrum.append('low_loss_model')
                add_difference = True
                anglog, _, _ = eels_tools.angle_correction(spectrum)
                parameter = list(self.parent.dataset.metadata['plasmon']['parameter'][x, y])
                low_loss = eels_tools.multiple_scattering(energy_scale, parameter)#  * anglog
                additional_spectra['low_loss_model'] = low_loss
                additional_spectra['difference'] = np.array(spectrum) - np.array(low_loss)
                
        if self.plot_zlButton.isChecked():
            if 'zero_loss' in self.parent.dataset.metadata:
                if 'zero_loss' not in self.parent.add_spectrum:
                    self.parent.add_spectrum.append('zero_loss')
                parameter = self.parent.dataset.metadata['zero_loss']['parameter'][x, y]
                zero_loss  = eels_tools.zero_loss_function(energy_scale, parameter)
                additional_spectra['zero_loss'] = zero_loss
                additional_spectra['difference'] -= np.array(zero_loss)
                add_difference = True
        if not add_difference:
            additional_spectra.pop('difference')
        
        return dict(reversed(additional_spectra.items()))
            

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

    
    def set_fit_width(self):
        pass
    
    def set_dataset(self):
        item_text = self.mainList.currentText()
        if item_text == 'None':
            return
        self.parent.main = item_text.split(':')[0]
        self.ll_key = self.parent.main
        self.parent.datasets['_relationship']['low_loss'] = self.ll_key
        self.parent.set_dataset()
    
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
        print(self.parent.intensity_scale)   
        self.parent.plotUpdate()

    def get_resolution_function(self):
        zero_loss_fit_width = float(self.fit_widthEdit.displayText())
        if 'zero_loss' not in self.parent.dataset.metadata.keys():
            self.parent.dataset.metadata['zero_loss'] = {}
        self.parent.dataset.metadata['plot']['additional_spectra']= []
        self.parent.dataset.metadata['plot']['additional_features']= []
            
        spectrum = self.get_spectrum()
        if self.parent.dataset.data_type.name == 'SPECTRUM':
            self.parent.dataset.metadata['zero_loss']['parameter'] = np.zeros([1,1,6])
            self.parent.dataset.metadata['plot']['x'] = 0
            self.parent.dataset.metadata['plot']['y'] = 0   
        else:
            if 'parameter' not in self.parent.dataset.metadata['zero_loss']:
                self.parent.dataset.metadata['zero_loss']['parameter'] = np.zeros([self.parent.dataset.shape[0], self.parent.dataset.shape[1], 6])
        
        res  = eels_tools.get_resolution_functions(spectrum, startFitEnergy=-zero_loss_fit_width, endFitEnergy=zero_loss_fit_width)
        
        self.parent.dataset.metadata['zero_loss'].update({'fit_start': -zero_loss_fit_width, 'fit_end': zero_loss_fit_width})
        self.parent.dataset.metadata['zero_loss']['parameter'][self.parent.x, self.parent.y] = res.metadata['zero_loss']['fit_parameter']
        
        self.plot_zlButton.setChecked(True)
        self.multi_thicknessEdit.setText(f"{np.log(spectrum.sum()/res.sum()):.4f}")
        self.parent.status.showMessage('Fitted zero-loss peak')

        self.parent.dataset.metadata['plot']['additional_spectra'] = ['LowLoss']
        self.update_ll_plot()
        self.parent.status.showMessage('Fitted zero-loss peak: relative thickness: {self.multi_thicknessEdit.displayText()} * inelastic MFP')

    
    def get_drude(self, value=0):
        self.plot_drudeButton.setChecked(False)

        if self.parent.dataset.data_type.name == 'SPECTRUM':
            self.parent.x = 0
            self.parent.y = 0
        fit_start = float(self.drude_startEdit.displayText())
        fit_end = float(self.drude_endEdit.displayText())   
        if 'plasmon' not in self.parent.dataset.metadata.keys():
            self.parent.dataset.metadata['plasmon'] = {}
        if 'parameter' not in self.parent.dataset.metadata['plasmon'].keys():
            if len(self.parent.dataset.shape) > 2:
                self.parent.dataset.metadata['plasmon']['parameter'] = np.zeros([self.parent.dataset.shape[0], self.parent.dataset.shape[1], 4])
                self.parent.dataset.metadata['plasmon']['IMFP'] = np.zeros([self.parent.dataset.shape[0], self.parent.dataset.shape[1]])
            else:
                self.parent.dataset.metadata['plasmon']['parameter'] = np.zeros([1, 1, 4])
        self.parent.dataset.metadata['plasmon']['fit_start'] = fit_start
        self.parent.dataset.metadata['plasmon']['fit_end'] = fit_end

        spectrum = self.parent.get_spectrum_dataset()    
        plasmon = eels_tools.fit_plasmon(spectrum, fit_start, fit_end)
        
        p = plasmon.metadata['plasmon']['parameter']
        p = list(np.abs(p))
        p.append(float(self.multi_thicknessEdit.displayText()))
        self.parent.dataset.metadata['plasmon']['parameter'][self.parent.x, self.parent.y] = p
        
        self.plot_drudeButton.setChecked(True)        
        self.drude_energyEdit.setText(f"{np.abs(p[0]):.3}")
        self.drude_widthEdit.setText(f"{np.abs(p[1]):.3}")
        self.drude_amplitudeEdit.setText(f"{np.abs(p[2]):.3}")
        
        _, dsdo, _ = eels_tools.angle_correction(spectrum)

        I0 = spectrum.sum()
        # T = m_0 v**2 !!!  a_0 = 0.05292 nm p[2] = S(E)/elf
        t_nm  = p[2]/I0*dsdo  #Egerton equ 4.26% probability per eV
        relative_thickness = float(self.multi_thicknessEdit.displayText())
        imfp, _ = eels_tools.inelatic_mean_free_path(p[0], spectrum)
        t_nm = float(relative_thickness * imfp)
        self.parent.status.showMessage(f'Fitted plasmon peak: thickness :{t_nm:.1f} nm and IMFP: {t_nm/relative_thickness:.1f} nm in free electron approximation')

        """
                self.parent.datasets['plasmon'].metadata['plasmon']['thickness'] = t_nm
            self.parent.datasets['plasmon'].metadata['plasmon']['relative_thickness'] = relative_thickness
            self.parent.datasets['plasmon'].metadata['plasmon']['IMFP'] = t_nm/relative_thickness
        """
        self.parent.dataset.metadata['plot']['additional_spectra'] = ['LowLoss']
        
        self.update_ll_plot()
        self.parent.status.showMessage('Fitting plasmon peak')

    def multiple_scattering(self, value=0):
        if self.parent.dataset.ndim >1:
            anglog, dsdo, _ = eels_tools.angle_correction(self.parent.spectrum)
            par = np.array(self.parent.datasets['plasmon'].metadata['plasmon']['parameter'])
            for x in range(self.parent.dataset.shape[0]):
                for y in range(self.parent.dataset.shape[1]):
                    self.parent.datasets['low_loss_model'][x, y] = eels_tools.multiple_scattering(self.parent.energy_scale, par[x, y]) * anglog
        

    def do_all(self, value=0):
        if len(self.parent.dataset.shape) < 3:
            return
            
        zero_loss_fit_width=self.low_loss_tab[2, 0].value
        fit_start = self.low_loss_tab[5, 0].value
        fit_end = self.low_loss_tab[6, 0].value
        
        
        if 'low_loss_model' not in self.parent.datasets.keys():
            self.parent.datasets['low_loss_model'] = self.parent.dataset.copy()*0
            self.parent.datasets['low_loss_model'].title = self.parent.dataset.title + ' low_loss_model'
        
        self.low_loss_tab[15,1].max = self.parent.dataset.shape[0]*self.parent.dataset.shape[1]
        
        self.parent.datasets['zero_loss']  = eels_tools.get_resolution_functions(self.parent.dataset, startFitEnergy=-zero_loss_fit_width, endFitEnergy=zero_loss_fit_width)
        self.parent.datasets['zero_loss'].title = self.parent.dataset.title + ' zero_loss'
        self.parent.status.showMessage('Fitted zero-loss peak')

        self.parent.datasets['plasmon'] = eels_tools.fit_plasmon(self.parent.dataset, fit_start, fit_end)
        self.parent.datasets['plasmon'].title = self.parent.dataset.title + ' plasmon'
        
        self.parent.status.showMessage('Fitted zero-loss + plasmon peak')

        
        """
        anglog, _, _ = eels_tools.angle_correction(self.parent.spectrum)
        i = 0
        for x in range(self.parent.dataset.shape[0]):   
            for y in range(self.parent.dataset.shape[1]):
                self.low_loss_tab[15,1].value = i
                i+= 1

                spectrum = self.parent.dataset[x, y]
                
                plasmon = eels_tools.fit_plasmon(spectrum, fit_start, fit_end)
                p =np.abs(plasmon.metadata['plasmon']['parameter'])
                p = list(np.abs(p))
                
                p.append(np.log(spectrum.sum()/self.parent.datasets['zero_loss'][x,y].sum()))
                if p[-1] is np.nan:
                    p[-1] = 0
                low_loss = eels_tools.multiple_scattering(self.parent.energy_scale, p) * anglog
                self.parent.datasets['plasmon'][x, y] = np.array(plasmon.compute())
                self.parent.datasets['low_loss_model'][x, y] = np.array(low_loss)
                drude_p[x, y, :] = np.array(p)

       

        self.parent.datasets['plasmon'].metadata['plasmon'].update({'parameter': drude_p})
        self.parent.datasets['low_loss_model'].metadata['low_loss'] = ({'parameter': drude_p})
        """

        imfp = np.log(self.parent.dataset.sum(axis=2)/self.parent.datasets['zero_loss'].sum(axis=2)) 
        self.parent.dataset.metadata['plasmon']['parameter'] = np.append(self.parent.dataset.metadata['plasmon']['parameter'], imfp[..., np.newaxis], axis=2)
        E_p = self.parent.dataset.metadata['plasmon']['parameter'][:,:,0]    
        self.parent.datasets['plasmon'].metadata['plasmon']['IMFP'], _ = eels_tools.inelatic_mean_free_path(E_p, self.parent.spectrum)
        self.parent.datasets['_relationship']['zero_loss'] = 'zero_loss'
        self.parent.datasets['_relationship']['plasmon'] = 'plasmon'
        self.multiple_scattering()        
        self.parent.datasets['_relationship']['low_loss_model'] = 'low_loss_model'
        
        self.plot_dielectricButton.setChecked(False)            
    def get_multiple_scattering(self, value=0):
        self.plot_multiButton.setChecked(False)

        spectrum = self.get_spectrum()
        fit_start = float(self.multi_startEdit.displayText())
        fit_end = float(self.multi_endEdit.displayText())
        
        p = [float(self.drude_energyEdit.displayText()), float(self.drude_widthEdit.displayText()), float(self.drude_amplitudeEdit.displayText()), float(self.multi_thicknessEdit.displayText())]
        low_loss = eels_tools.fit_multiple_scattering(spectrum, fit_start, fit_end, pin=p)
        

        self.parent.datasets['multiple_scattering'] = low_loss
        self.parent.datasets['multiple_scattering'].title = 'multiple scattering'
        
        self.parent.datasets['_relationship']['multiple_scattering'] = 'multiple_scattering'
       
        self.plot_drudeButton.setChecked(False)
        self.plot_multiButton.setChecked(True)
        p = low_loss.metadata['multiple_scattering']['parameter']
        self.multi_thicknessEdit.setText(f"{p[3]:.3f}")
        
        self.parent.status.showMessage('Fitted multiple scattering')
        
        self.parent.dataset.metadata['plot']['additional_spectra'] = ['LowLoss']
        
        self.update_ll_plot()
        self.parent.status.showMessage('Fitting zero-loss peak: relative thickness: {self.multi_thicknessEdit.displayText()} * inelastic MFP')

        return low_loss
        
        
    def on_drude_energy_enter(self):
        if 'plasmon' in self.parent.dataset.metadata.keys():
            if len(self.parent.dataset.shape) > 2:
                self.parent.dataset.metadata['plasmon']['parameter'][self.parent.x, self.parent.y][0] = float(self.drude_startEdit.displayText())
            else:
                self.parent.dataset.metadata['plasmon']['parameter'][0, 0][0] = float(self.drude_startEdit.displayText())
            self.update_ll_plot()            

    def on_drude_width_enter(self):
        if 'plasmon' in self.parent.dataset.metadata.keys():
            if len(self.parent.dataset.shape) > 2:
                self.parent.dataset.metadata['plasmon']['parameter'][self.parent.x, self.parent.y][1] = float(self.drude_startEdit.displayText())
            else:
                self.parent.dataset.metadata['plasmon']['parameter'][0, 0][1] = float(self.drude_startEdit.displayText())
            self.update_ll_plot()            

    def on_drude_amplitude_enter(self):
        if 'plasmon' in self.parent.dataset.metadata.keys():
            if len(self.parent.dataset.shape) > 2:
                self.parent.dataset.metadata['plasmon']['parameter'][self.parent.x, self.parent.y][2] = float(self.drude_startEdit.displayText())
            else:
                self.parent.dataset.metadata['plasmon']['parameter'][0, 0][2] = float(self.drude_startEdit.displayText())
            self.update_ll_plot()            
        
    def on_multi_thickness_enter(self):
        if 'plasmon' in self.parent.dataset.metadata.keys():
            if len(self.parent.dataset.shape) > 2:
                self.parent.dataset.metadata['plasmon']['parameter'][self.parent.x, self.parent.y][3] = float(self.multi_thicknessEdit.displayText())
            else:
                self.parent.dataset.metadata['plasmon']['parameter'][0, 0][3] = float(self.multi_thicknessEdit.displayText())
            self.update_ll_plot()            