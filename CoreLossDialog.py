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
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import pyqtgraph as pg

import numpy as np
import sidpy
import scipy

from pyTEMlib import eels_tools

from periodic_table import PeriodicTable

class CoreLossDialog(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(CoreLossDialog, self).__init__(parent)
    
        self.parent = parent
        layout = self.get_sidbar()
        self.setLayout(layout)    
        self.setWindowTitle("Core Loss")
        self.cl_key = ''
        self.parent = parent
        self.dataset = parent.dataset
        self.name = 'CoreLoss'
        self.model = []
        self.edges = {}
        self.count = 0
        self.cl_key = 'None'
        
        self.number_of_edges = 0

        self.elements_selected = []
        self.periodic_table = PeriodicTable(self)

    def get_sidbar(self): 
        validfloat = QtGui.QDoubleValidator()
        validint = QtGui.QIntValidator()        
        
        layout = QtWidgets.QGridLayout()
        row = 0 
        self.mainList = QtWidgets.QComboBox(self)
        self.mainList.addItem("None")
        layout.addWidget(self.mainList,  row,0, 1, 3)
        layout.setColumnStretch(0, 3)  

        self.mainList.activated[str].connect(self.update_cl_dataset)
        
        row += 1
        self.fit_areaButton = QtWidgets.QPushButton()
        self.fit_areaButton.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.fit_areaButton.setText("Fit Area")
        layout.addWidget(self.fit_areaButton,  row,0, 1, 3)
        layout.setColumnStretch(0, 3) 
        self.fit_areaButton.setCheckable(True)
        self.fit_areaButton.clicked.connect(self.set_fit_area)
        
        row += 1
        self.fit_startLabel = QtWidgets.QLabel("Start Fit")
        self.fit_startEdit = QtWidgets.QLineEdit(" 3.0")
        # self.fit_startEdit.setValidator(validfloat)
        #self.fit_startEdit.editingFinished.connect(self.on_drude_start_enter)
        self.fit_startUnit = QtWidgets.QLabel("eV")
        layout.addWidget(self.fit_startLabel,row,0)
        layout.addWidget(self.fit_startEdit,row,1)
        layout.addWidget(self.fit_startUnit,row,2)

        row += 1
        self.fit_endLabel = QtWidgets.QLabel("End Fit")
        self.fit_endEdit = QtWidgets.QLineEdit(" 30.0")
        self.fit_endEdit.setValidator(validfloat)
        self.fit_endUnit = QtWidgets.QLabel("eV")
        layout.addWidget(self.fit_endLabel,row,0)
        layout.addWidget(self.fit_endEdit,row,1)
        layout.addWidget(self.fit_endUnit,row,2)

        row += 1
        self.elementsButton = QtWidgets.QPushButton()
        self.elementsButton.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.elementsButton.setText("Elements")
        layout.addWidget(self.elementsButton,  row,0, 1, 3)
        layout.setColumnStretch(0, 3) 
        self.elementsButton.clicked.connect(self.find_elements)
       
        row +=1
        self.edgeList = QtWidgets.QComboBox(self)
        self.edgeList.addItem("Edge 1")
        self.edgeList.addItem("add Edge") 
        layout.addWidget(self.edgeList,  row, 1)
        self.edgeList.activated[str].connect(self.update)

        row += 1
        self.element_zLabel = QtWidgets.QLabel("Element")
        self.element_zEdit = QtWidgets.QLineEdit(" 0")
        self.element_zEdit.setValidator(validint)
        self.element_zEdit.editingFinished.connect(self.update)
        self.element_zUnit = QtWidgets.QLabel("H")
        layout.addWidget(self.element_zLabel,row,0)
        layout.addWidget(self.element_zEdit,row,1)
        layout.addWidget(self.element_zUnit,row,2)

        row +=1
        self.symmetryLabel = QtWidgets.QLabel("Symmetry")
        self.symmetryList = QtWidgets.QComboBox(self)
        self.symmetry_options=['K1', 'L3', 'M5', 'M3', 'M1', 'N7', 'N5', 'N3', 'N1']
        self.symmetryList.addItems(self.symmetry_options) 
        layout.addWidget(self.symmetryList,  row, 1)
        
        
        row +=1
        self.edge_onsetLabel = QtWidgets.QLabel("Onset")
        self.edge_onsetEdit = QtWidgets.QLineEdit(" 5.0")
        self.edge_onsetEdit.setValidator(validfloat)
        self.edge_onsetEdit.editingFinished.connect(self.on_onset_enter)
        self.edge_onsetUnit = QtWidgets.QLabel("eV")
        layout.addWidget(self.edge_onsetLabel,row,0)
        layout.addWidget(self.edge_onsetEdit,row,1)
        layout.addWidget(self.edge_onsetUnit,row,2)

        row += 1
        self.edge_excl_startLabel = QtWidgets.QLabel("Excl.Start:")
        self.edge_excl_startEdit = QtWidgets.QLineEdit(" 5.0")
        self.edge_excl_startEdit.setValidator(validfloat)
        self.edge_excl_startEdit.editingFinished.connect(self.on_excl_start_enter)
        self.edge_excl_startUnit = QtWidgets.QLabel("eV")
        layout.addWidget(self.edge_excl_startLabel,row,0)
        layout.addWidget(self.edge_excl_startEdit,row,1)
        layout.addWidget(self.edge_excl_startUnit,row,2)

        row += 1
        self.edge_excl_endLabel = QtWidgets.QLabel("Excl.End")
        self.edge_excl_endEdit = QtWidgets.QLineEdit(" 5.0")
        self.edge_excl_endEdit.setValidator(validfloat)
        self.edge_excl_endEdit.editingFinished.connect(self.on_excl_end_enter)
        self.edge_excl_endUnit = QtWidgets.QLabel("eV")
        layout.addWidget(self.edge_excl_endLabel,row,0)
        layout.addWidget(self.edge_excl_endEdit,row,1)
        layout.addWidget(self.edge_excl_endUnit,row,2)

        row += 1
        self.edge_multiplierLabel = QtWidgets.QLabel("Multiplier")
        self.edge_multiplierEdit = QtWidgets.QLineEdit(" 5.0")
        self.edge_multiplierEdit.setValidator(validfloat)
        self.edge_multiplierEdit.editingFinished.connect(self.on_multiplier_enter)
        self.edge_multiplierUnit = QtWidgets.QLabel("a.u.")
        layout.addWidget(self.edge_multiplierLabel,row,0)
        layout.addWidget(self.edge_multiplierEdit,row,1)
        layout.addWidget(self.edge_multiplierUnit,row,2)

        row += 1
        self.quantifyButton = QtWidgets.QPushButton()
        self.quantifyButton.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.quantifyButton.setText("Quantification")
        layout.addWidget(self.quantifyButton,  row,0, 1, 3)
        layout.setColumnStretch(0, 3)       
        self.quantifyButton.clicked.connect(self.do_fit)
         
        row += 1
        self.conv_LL_Button = QtWidgets.QPushButton()
        self.conv_LL_Button.setText("Conv.LL")
        self.conv_LL_Button.setCheckable(True)
        layout.addWidget(self.conv_LL_Button,  row, 0)
        # self.conv_LL_Button.clicked.connect(self.update_ll_plot)

        self.probabilityButton = QtWidgets.QPushButton()
        self.probabilityButton.setText("Probability")
        self.probabilityButton.setCheckable(True)
        layout.addWidget(self.probabilityButton,  row, 2)
        self.probabilityButton.clicked.connect(self.set_intensity_scale)

        self.show_edgesButton = QtWidgets.QPushButton()
        self.show_edgesButton.setText("Show Edges")
        self.show_edgesButton.setCheckable(True)
        layout.addWidget(self.show_edgesButton,  row, 1)
        self.show_edgesButton.clicked.connect(self.update_cl_plot)
        
        row += 1
        self.plot_edgesButton = QtWidgets.QPushButton()
        self.plot_edgesButton.setText("Plot Model")
        self.plot_edgesButton.setCheckable(True)
        layout.addWidget(self.plot_edgesButton,  row, 0)
        self.plot_edgesButton.clicked.connect(self.update_cl_plot)

        self.do_allButton = QtWidgets.QPushButton()
        self.do_allButton.setText("Do All")
        self.do_allButton.setCheckable(True)
        layout.addWidget(self.do_allButton,  row, 2)

        return layout
        
    def update_cl_sidebar(self):
        if '_relationship' not in self.parent.datasets:
            return
        spectrum_list = ['None']
        cl_index = 0
        if 'core_loss' in self.parent.datasets['_relationship']:
            self.cl_key = self.parent.datasets['_relationship']['core_loss']
        else:
            self.cl_key = 'None'

        for index, key in enumerate(self.parent.datasets.keys()):
            if isinstance(self.parent.datasets[key], sidpy.Dataset):
                if 'SPECTR' in self.parent.datasets[key].data_type.name:
                    spectrum_list.append(f'{key}: {self.parent.datasets[key].title}')
                if key == self.cl_key:
                    cl_index = index + 1

        if cl_index >len(spectrum_list) - 1:
            cl_index = len(spectrum_list) - 1
        self.mainList.clear()
        for item in spectrum_list:
            self.mainList.addItem(item)
        self.mainList.setCurrentIndex(cl_index)
        
        self.update_cl_dataset()
        
    def update_cl_dataset(self, value=0):
        self.cl_key = self.mainList.currentText().split(':')[0]
        if self.cl_key not in self.parent.datasets.keys():
            return
        self.parent.coreloss_key = self.cl_key
        if 'None' in self.cl_key:
            return
        self.parent.main = self.cl_key
        self.parent.set_dataset()
        self.dataset = self.parent.dataset
        self.parent.datasets['_relationship']['core_loss'] = self.cl_key
        self.set_edges()
        self.parent.plotUpdate()
        self.update()

    def set_edges(self):
        if 'core_loss' not in self.parent.dataset.metadata:
            if 'fit_area' not in self.edges:
                self.parent.dataset.metadata['core_loss'] = {}
            else:
                self.parent.dataset.metadata['core_loss'] = self.edges.copy()

        self.edges = self.parent.dataset.metadata['core_loss']
        
        if 'fit_area' not in self.edges:
            energy_scale = self.parent.dataset.get_spectral_dims(return_axis=True)[0].values
            self.edges['fit_area']={'fit_start': energy_scale[1], 
                                    'fit_end': energy_scale[-2]}
           
        self.fit_startEdit.setText(f"{self.edges['fit_area']['fit_start']:.3f}")
        self.fit_endEdit.setText(f"{self.edges['fit_area']['fit_end']:.3f}")
        
        
    def update_cl_plot(self):
        self.parent.dataset.metadata['plot']['additional_features'] = 'CoreLoss'
        self.parent.plotUpdate()

    def set_fit_area(self):
        if not self.fit_areaButton.isChecked():
            for key, region in self.parent.plot_features.items():
                if 'exclude' in key:
                    index = key.split('_')[1]
                    span = region.getRegion()
                    self.edges[index]['start_exclude'] = span[0]
                    self.edges[index]['end_exclude'] = span[1]
                if 'fit_area' in key:
                    span = region.getRegion()
                    self.edges['fit_area']['fit_start'] = span[0]
                    self.edges['fit_area']['fit_end'] = span[1]
        self.update()
        self.update_cl_plot()
        
    def update_element(self, z=0, index=-1):
        # We check whether this element is already in the list
        if z == 0:
            z = int(self.edge_zEdit.displayText())

        zz = eels_tools.get_z(z)
        for key, edge in self.edges.items():
            if key.isdigit():
                if 'z' in edge:
                    if zz == edge['z']:
                        return False

        major_edge = ''
        minor_edge = ''
        all_edges = {}
        energy_scale = self.parent.dataset.get_spectral_dims(return_axis=True)[0]
        x_section = eels_tools.get_x_sections(zz)
        edge_start = 10  # int(15./ft.get_slope(self.energy_scale)+0.5)
        
        for key in x_section:
            if len(key) == 2 and key[0] in ['K', 'L', 'M', 'N', 'O'] and key[1].isdigit():
                if energy_scale[edge_start] < x_section[key]['onset'] < energy_scale[-edge_start]:
                    if key in ['K1', 'L3', 'M5']:
                        major_edge = key
                    elif key in self.symmetry_options:
                        if minor_edge == '':
                            minor_edge = key
                        if int(key[-1]) % 2 > 0:
                            if int(minor_edge[-1]) % 2 == 0 or key[-1] > minor_edge[-1]:
                                minor_edge = key

                    all_edges[key] = {'onset': x_section[key]['onset']}

        if major_edge != '':
            key = major_edge
        elif minor_edge != '':
            key = minor_edge
        else:
            print(f'Could not find no edge of {zz} in spectrum')
            return False
        
        if index == -1:
            item = self.edgeList.currentText()
            if item == 'add Edge':
                self.number_of_edges +=1
                index = self.number_of_edges
                self.edgeList.insertItem(-2, (f'Edge {index}', index))
            else:
                index = int(item.split(' ')[-1])
        
        if str(index) not in self.edges:
            self.edges[str(index)] = {}

        start_exclude = x_section[key]['onset'] - x_section[key]['excl before']
        end_exclude = x_section[key]['onset'] + x_section[key]['excl after']

        self.edges[str(index)] = {'z': zz, 'symmetry': key, 'element': eels_tools.elements[zz],
                                  'onset': x_section[key]['onset'], 'end_exclude': end_exclude,
                                  'start_exclude': start_exclude}
        self.edges[str(index)]['all_edges'] = all_edges
        self.edges[str(index)]['chemical_shift'] = 0.0
        self.edges[str(index)]['areal_density'] = 0.0
        self.edges[str(index)]['original_onset'] = self.edges[str(index)]['onset']
        return True

    def find_elements(self, value=0):
        value = int(self.element_zEdit.displayText())
        if '0' not in self.edges:
            self.edges['0'] = {}
        
        if value == 0:
            selected_elements = []
            elements = self.edges.copy()

            for key in self.edges:
                if key.isdigit():
                    if 'element' in self.edges[key]:
                        selected_elements.append(self.edges[key]['element'])
            self.periodic_table.elements_selected = selected_elements
            self.periodic_table.exec()
            self.elements_selected = self.periodic_table.elements_selected
        self.set_elements()
    
    def sort_elements(self):
        onsets = []
        for index, edge in self.edges.items():
            if index.isdigit():
                onsets.append(float(edge['onset']))
        arg_sorted = np.argsort(onsets)
        edges = self.edges.copy()
        for index, i_sorted in enumerate(arg_sorted):
            self.edges[str(index)] = edges[str(i_sorted)].copy()
        index = 0
        edge = self.edges['0']
        energy_scale = self.parent.dataset.get_spectral_dims(return_axis=True)[0]
        dispersion = energy_scale[1]-energy_scale[0]

        while str(index + 1) in self.edges:
            next_edge = self.edges[str(index + 1)]
            if edge['end_exclude'] > next_edge['start_exclude'] - 5 * dispersion:
                edge['end_exclude'] = next_edge['start_exclude'] - 5 * dispersion
            edge = next_edge
            index += 1

        if edge['end_exclude'] > energy_scale[-3]:
            edge['end_exclude'] = energy_scale[-3]

    def set_elements(self, value=0):
        selected_elements = self.elements_selected
        edges = self.edges.copy()
        to_delete = []
        old_elements = []
        if len(selected_elements) > 0:
            for key in self.edges:
                if key.isdigit():
                    if 'element' in self.edges[key]:
                        to_delete.append(key)
                        old_elements.append(self.edges[key]['element'])
        for key in to_delete:
            edges[key] = self.edges[key]
            del self.edges[key]
        for index, elem in enumerate(selected_elements):
            if elem in old_elements:
                self.edges[str(index)] = edges[str(old_elements.index(elem))]
            else:
                self.update_element(elem, index=index)
        self.sort_elements()
        self.edgeList.clear()
        self.edgeList.addItem('setting')
        self.edgeList.setCurrentIndex(0)
        self.update()

    def update(self, index=0):
        self.dataset = self.parent.dataset
        item = self.edgeList.currentText()
        if item == 'add Edge':
            index = self.edgeList.count()
            self.edges[str(index)] = {'z': 0,  'element': 'x', 'symmetry': 'K1', 'onset': 0, 'start_exclude': 0, 'end_exclude': 0,
                                      'areal_density': 0, 'chemical_shift': 0}
            self.edgeList.insertItem(index, f'Edge {int(index)}')   
        else:
            index = self.edgeList.currentIndex()
        self.edgeList.clear()
        for key in self.edges:
            if key.isdigit():
                self.edgeList.addItem(f'Edge {int(key)+1}')
        self.edgeList.setCurrentIndex(index)
        self.edgeList.addItem('add Edge')
               
        self.number_of_edges = self.edgeList.count() - 1
        if str(index) not in self.edges:
            self.edges[str(index)] = {'z': 0,  'element': 'x', 'symmetry': 'K1', 'onset': 0, 'start_exclude': 0, 'end_exclude': 0,
                                      'areal_density': 0, 'chemical_shift': 0}
        if 'z' not in self.edges[str(index)]:
            self.edges[str(index)] = {'z': 0,  'element': 'x', 'symmetry': 'K1', 'onset': 0, 'start_exclude': 0, 'end_exclude': 0,
                                      'areal_density': 0, 'chemical_shift': 0}
        edge = self.edges[str(index)]
        
        energy_scale = self.parent.dataset.get_spectral_dims(return_axis=True)[0]
        self.element_zEdit.setText(str(edge['z']))
        self.element_zUnit.setText(edge['element'])
        self.symmetryList.setCurrentText(edge['symmetry'])
        self.edge_onsetEdit.setText(f"{edge['onset']:.3f}")
        self.edge_excl_startEdit.setText(f"{edge['start_exclude']:.3f}")
        self.edge_excl_endEdit.setText(f"{edge['end_exclude']:.3f}")
        # self.core_loss_tab[13, 0].value = self.parent.info_tab[9, 2].value
        self.probabilityButton.setChecked(self.parent.InfoDialog.quantifyButton.isChecked())
        if self.parent.intensity_scale == 1.0:
            self.edge_multiplierEdit.setText(f"{edge['areal_density']:.1f}")
            self.edge_multiplierUnit.setText('a.u.')
        else:
            dispersion = energy_scale[1] - energy_scale[0]
            self.edge_multiplierEdit.setText(f"{edge['areal_density']/self.dataset.metadata['experiment']['flux_ppm']*1e-6:.2f}")
            self.edge_multiplierUnit.setText('atoms/nm²')

    def set_dataset(self):
        item_text = self.mainList.currentText()
        if item_text == 'None':
            return
        self.parent.main = item_text.split(':')[0]
        self.cl_key = self.parent.main
        self.parent.datasets['_relationship']['core_loss'] = self.cl_key
        self.parent.set_dataset()
        self.dataset = self.parent.dataset
        self.parent.plotUpdate()
    
    def set_intensity_scale(self, checked):
        self.parent.intensity_scale = 1.0
        checked = self.probabilityButton.isChecked()
        self.parent.InfoDialog.quantifyButton.setChecked(checked)
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

    def get_additional_spectra(self):        
        spectrum = self.parent.get_spectrum_dataset()
        energy_scale = spectrum.get_spectral_dims(return_axis=True)[0].values
        x = self.parent.x
        y = self.parent.y

        additional_spectra = {}
        if 'core_loss' in self.parent.dataset.metadata:
            x = self.parent.x
            y = self.parent.y
            p = self.parent.dataset.metadata['core_loss']['parameter'][x, y]
            xsec = self.parent.dataset.metadata['core_loss']['xsections']
            number_of_edges = xsec.shape[0]
            self.parent.dataset.metadata['core_loss']['parameter'][x, y] = p                             
            model = eels_tools.core_loss_model(energy_scale, p, number_of_edges, xsec)
            additional_spectra['core-loss model'] =  model
            additional_spectra['difference'] = np.array(spectrum) - model

            #self.additional_features()
        return additional_spectra
    
    def get_additional_features(self):
        plot_features = {}
        if self.fit_areaButton.isChecked():        
            plot_features["fit_area"] = pg.LinearRegionItem(values=(self.edges['fit_area']['fit_start'], self.edges['fit_area']['fit_end']), brush=(0, 150, 0, 40))    
            for key, edge in self.parent.dataset.metadata['core_loss'].items():
                if key.isdigit():
                    plot_features[f"edge_{key}_exclude"] = pg.LinearRegionItem(values=(edge['start_exclude'], edge['end_exclude']), brush=(150, 0, 0, 40))    
            
        if self.show_edgesButton.isChecked():
            spectrum = self.parent.get_spectrum_dataset()
            energy_scale = spectrum.get_spectral_dims(return_axis=True)[0].values
            
            for key, edge in self.parent.dataset.metadata['core_loss'].items():
                i = 0
                if key.isdigit():
                    element = edge['element']
                    for sym in edge['all_edges']:
                        x = edge['all_edges'][sym]['onset'] + \
                            edge['chemical_shift']
                        if energy_scale[1] < x < energy_scale[-2]:
                            label =f"{element}-{sym}"
                            plot_features[label] = pg.InfiniteLine(pos=x, angle=90, pen='gray', label=label, labelOpts={'position': 0.9, 
                                                                                                                        'movable':True})
                            #self.addItem(line)Line(x=x, pen='gray')
        return plot_features

    def do_fit(self, value=0):
        if 'experiment' in self.dataset.metadata:
            exp = self.dataset.metadata['experiment']
            if 'convergence_angle' not in exp:
                self.parent.status_message('Aborted Quantification: need a convergence_angle in experiment of metadata dictionary')
                return
    
            alpha = exp['convergence_angle']
            beta = exp['collection_angle']
            beam_kv = exp['acceleration_voltage']
            if beam_kv < 20:
                self.parent.status_message('Aborted Quantification: no acceleration voltage')
                return
        else:
            raise ValueError(
                'need an experiment parameter in metadata dictionary')
        if 'core_loss' not in self.parent.dataset.metadata.keys():
            self.parent.dataset.metadata['core_loss'] = {}
        self.number_of_edges = self.edgeList.count() - 1
    
        if 'parameter' not in self.parent.dataset.metadata['core_loss']:
            self.parent.dataset.metadata['core_loss']['parameter'] = np.zeros([1, 1, 1])
        if self.parent.dataset.metadata['core_loss']['parameter'].shape[2] < self.number_of_edges + 5:  
            if self.parent.dataset.data_type.name == 'SPECTRUM':
                self.parent.dataset.metadata['core_loss']['parameter'] = np.zeros([1, 1, self.number_of_edges+5])
                self.parent.x = 0
                self.parent.y = 0
            else:
                self.parent.dataset.metadata['core_loss']['parameter'] = np.zeros([self.parent.dataset.shape[0], 
                                                                                   self.parent.dataset.shape[1],
                                                                                   self.number_of_edges + 5])
        self.parent.status.showMessage('Fitting cross-sections ')
        energy_scale = self.dataset.get_spectral_dims(return_axis=True)[0].values
        eff_beta = eels_tools.effective_collection_angle(
            energy_scale, alpha, beta, beam_kv)
        self.dataset.metadata['experiment']['eff_beta'] = eff_beta
        self.low_loss = None
        if self.conv_LL_Button.isChecked():
            if 'low_loss' in self.parent.datasets['_relationship'].keys():
                ll_key = self.parent.datasets['_relationship']['low_loss']
                self.low_loss = np.array(self.parent.datasets[ll_key] / \
                                    self.parent.datasets[ll_key].sum())
        edges = eels_tools.make_cross_sections(self.edges, np.array(energy_scale), 
                                               beam_kv, eff_beta, self.low_loss)
        spectrum = self.parent.get_spectrum_dataset()
        self.edges['fit_area']={'fit_start': float(self.fit_startEdit.displayText()), 
                                'fit_end': float(self.fit_endEdit.displayText())}
        self.edges = eels_tools.fit_edges2(spectrum, energy_scale, edges)
        self.model = self.edges['model']['spectrum'].copy()

        
        areal_density = []
        elements = []
        for key in edges:
            if key.isdigit():  # only edges have numbers in that dictionary
                elements.append(edges[key]['element'])
                areal_density.append(edges[key]['areal_density'])
        areal_density = np.array(areal_density)
        out_string = 'Relative composition: '
        for i, element in enumerate(elements):
            out_string += f'{element}: {areal_density[i] / areal_density.sum() * 100:.1f}%  '
        self.parent.status.showMessage(out_string)
        self.parent.dataset.metadata['core_loss']['edges'] = {}
        for key in self.edges:
            if key.isdigit():
                self.parent.dataset.metadata['core_loss']['edges'][key] = {'z': self.edges[key]['z'],
                                                                        'element': self.edges[key]['element'],
                                                                        'onset': self.edges[key]['onset'],  
                                                                        'all_edges': self.edges[key]['all_edges'], 
                                                                        'chemical_shift': self.edges[key]['chemical_shift'],
                                                                        'original_onset': self.edges[key]['original_onset'],
                                                                        'start_exclude': self.edges[key]['start_exclude'],
                                                                        'end_exclude': self.edges[key]['end_exclude'],
                                                                        'areal_density': self.edges[key]['areal_density'],
                                                                        'symmetry': self.edges[key]['symmetry']}
                                                                        
        self.parent.dataset.metadata['core_loss']['fit_area'] = self.edges['fit_area']
        if self.low_loss is None:
            self.parent.dataset.metadata['core_loss']['low_loss'] = None
        else:
            self.parent.dataset.metadata['core_loss']['low_loss'] = self.parent.datasets['_relationship']['low_loss']  
        
        self.parent.dataset.metadata['core_loss']['xsections'] = self.edges['model']['xsec']
        self.parent.dataset.metadata['core_loss']['parameter'][self.parent.x, self.parent.y] = self.edges['model']['fit_parameter']
        
        
        self.update()
        self.parent.dataset.metadata['plot']['additional_spectra'] = 'CoreLoss'
        self.update_cl_plot()
        self.parent.status.showMessage('Fitting cross-sections -- success ' + out_string)

    def on_onset_enter(self):
        edge = self.edges[str(self.edgeList.currentIndex())]
        edge['onset'] = float(self.edge_onsetEdit.displayText())  
        if 'original_onset' in edge:
            edge['chemical_shift'] = edge['onset'] - edge['original_onset']
        self.update_cl_dataset()

    def on_excl_start_enter(self):
        self.edges[str(self.edgeList.currentIndex())]['start_exclude'] = float(self.edge_excl_startEdit.displayText())  

    def on_excl_end_enter(self):
        self.edges[str(self.edgeList.currentIndex())]['end_exclude'] = float(self.edge_excl_endEdit.displayText())  

    def on_multiplier_enter(self):
        edge = self.edges[str(self.edgeList.currentIndex())] * self.parent.intensity_scale
        
        edge['areal_density'] = float(self.edge_multiplierEdit.displayText())  
        if 'core_loss' in self.parent.dataset.metadata:
            if self.dataset.data_type.name == 'SPECTRUM':
                self.parent.x = 0
                self.parent.y = 0
            self.parent.dataset.metadata['core_loss']['parameter'][self.parent.x, self.parent.y][self.edgeList.currentIndex()+5] = float(self.edge_multiplierEdit.displayText())
        self.update_cl_plot()            
