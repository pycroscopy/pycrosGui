#####################################################################
#
# Part of pycrosGUI
# of pycroscopy ecosystem
#
# AtomDialog: Atom finding and analyzing dialog.
#       
# Author: Gerd Duscher, UTK
# started 02/2025
####################################################################
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5 import QtCore

import pyqtgraph as pg

import numpy as np
import sidpy
import scipy
import ase

from pyTEMlib import image_tools
import pyTEMlib.atom_tools
import pyTEMlib.crystal_tools
import pyTEMlib.graph_tools



class AtomDialog(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(AtomDialog, self).__init__(parent)
    
        self.parent = parent
        layout = self.get_sidbar()
        self.atoms = None
        self.setLayout(layout)    
        self.name = 'Atoms'
        self.setWindowTitle(self.name)
        
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
        self.regButton.setText("Find Atoms")
        layout.addWidget(self.regButton,  row,0, 1, 3)
        layout.setColumnStretch(0, 3) 
        #self.scaleButton.clicked.connect(self.rigi_registration)
        
        row += 1
        self.atomSize_label = QtWidgets.QLabel("Atom size")
        self.atomSize_edit = QtWidgets.QLineEdit("0.1")
        self.atomSize_edit.setValidator(validfloat)
        self.atomSize_unit = QtWidgets.QLabel("A")
        layout.addWidget(self.atomSize_label,row,0)
        layout.addWidget(self.atomSize_edit,row,1)
        layout.addWidget(self.atomSize_unit,row,2)
        
        
        row += 1
        self.slider = QtWidgets.QSlider()
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.slider.setMaximum(100)
        self.slider.setMinimum(1)
        self.slider.setValue(74)
        layout.addWidget(self.slider,row,1)
        
        row += 1
        self.atomThreshold_label = QtWidgets.QLabel("Threshold")
        
        self.atomThreshold_edit = QtWidgets.QLineEdit("0.5")
        
        self.atomThreshold_edit.setValidator(validfloat)
        layout.addWidget(self.atomThreshold_label,row,0)
        layout.addWidget(self.atomThreshold_edit,row,1)
        
        row += 1
        self.atomsButton = QtWidgets.QPushButton()
        self.atomsButton.setText("Find Atoms")
        self.atomsButton.setCheckable(True)
        layout.addWidget(self.atomsButton,  row, 0)
        self.atomsButton.clicked.connect(self.find_atoms)
        
        self.refineButton = QtWidgets.QPushButton()
        self.refineButton.setText("Refine Atoms")
        self.refineButton.setCheckable(True)
        layout.addWidget(self.refineButton,  row, 1)
        
        row += 1 
        self.copyToList = QtWidgets.QComboBox(self)
        self.copyToList.addItem("None")
        layout.addWidget(self.copyToList,  row,1, 2, 3)
        layout.setColumnStretch(1, 3)  
        self.copyToList.activated[str].connect(self.copy_atoms_to)
        self.copyAtom_label = QtWidgets.QLabel("Copy atoms")
        layout.addWidget(self.copyAtom_label,row,0)
        
        row += 1
        self.clusterButton =  QtWidgets.QPushButton()
        self.clusterButton.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.clusterButton.setText("Cluster Tools")
        layout.addWidget(self.clusterButton,  row,0, 1, 3)
        layout.setColumnStretch(0, 3) 
        # self.scaleButton.clicked.connect(self.cursor2energy_scale)
       
        row += 1
        self.graphButton =  QtWidgets.QPushButton()
        self.graphButton.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.graphButton.setText("Graph Tools")
        layout.addWidget(self.graphButton,  row,0, 1, 3)
        layout.setColumnStretch(0, 3) 
        # self.scaleButton.clicked.connect(self.cbreath_first)
        
        row += 1
        self.startAtom_x_label = QtWidgets.QLabel("Start Atom x")
        self.startAtom_x_edit = QtWidgets.QLineEdit("0.1")
        self.startAtom_x_edit.setValidator(validfloat)
        # self.startAtom_x_edit.editingFinished.connect(self.set_resolution)
        self.startAtom_x_unit = QtWidgets.QLabel("nm")
        layout.addWidget(self.startAtom_x_label,row,0)
        layout.addWidget(self.startAtom_x_edit,row,1)
        layout.addWidget(self.startAtom_x_unit,row,2)
        
        row += 1
        self.startAtom_y_label = QtWidgets.QLabel("Start Atom y")
        self.startAtom_y_edit = QtWidgets.QLineEdit("0.1")
        self.startAtom_y_edit.setValidator(validfloat)
        # self.startAtom_y_edit.editingFinished.connect(self.set_resolution)
        self.startAtom_y_unit = QtWidgets.QLabel("nm")
        layout.addWidget(self.startAtom_y_label,row,0)
        layout.addWidget(self.startAtom_y_edit,row,1)
        layout.addWidget(self.startAtom_y_unit,row,2)
        
        row += 1 
        self.structureList = QtWidgets.QComboBox(self)
        structure_list = []
        for crystal in pyTEMlib.crystal_tools.crystal_data_base.values():
            structure_list.append(crystal['crystal_name'])
        self.structureList.addItems(sorted(set(structure_list)))
        layout.addWidget(self.structureList,  row,1, 2, 3)
        layout.setColumnStretch(1, 3)  
        self.structureList.activated[str].connect(self.set_structure)
        
        self.structure_label = QtWidgets.QLabel("Structures")
        layout.addWidget(self.structure_label,row,0)
        
        row += 1
        self.zoneAxis_label = QtWidgets.QLabel("Zone axis")
        self.zoneAxis_edit = QtWidgets.QLineEdit("0 0 1")
        # self.zoneAxis_edit.editingFinished.connect(self.set_resolution)
        self.zoneAxis_unit = QtWidgets.QLabel("h k l")
        layout.addWidget(self.zoneAxis_label,row,0)
        layout.addWidget(self.zoneAxis_edit,row,1)
        layout.addWidget(self.zoneAxis_unit,row,2)
        
        row += 1
        self.hoppButton = QtWidgets.QPushButton()
        self.hoppButton.setText("Hopp")
        self.hoppButton.setCheckable(True)
        layout.addWidget(self.hoppButton,  row, 0)
        self.hoppButton.clicked.connect(self.graph_hopp)
        
        self.polygonButton = QtWidgets.QPushButton()
        self.polygonButton.setText("Polygons")
        self.polygonButton.setCheckable(True)
        layout.addWidget(self.polygonButton,  row, 1)
        self.polygonButton.clicked.connect(self.find_atoms)
        
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
        self.parent.select_roi.sigRegionChangeFinished.connect(self.update_roi)
        self.parent.select_roi.visible = True
        self.parent.img.mouseClickEvent = self.mouseClickEvent

    def update_roi(self):
        self.startAtom_x_edit.setText(f"{self.parent.select_roi.pos().x()}")
        self.startAtom_y_edit.setText(f"{self.parent.select_roi.pos().y()}")
            
           
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
        

    def mouseClickEvent(self, ev):
        print('mouseClickEvent', ev.pos(), 'double', ev.double())
        if ev.double():
            pos = ev.pos()
            nm_pos = self.parent.img.mapToParent(pos)
            #pos = np.array([pos.x(), pos.y()])/10
            self.startAtom_y_edit.setText(f"{nm_pos.y():.2f}")
            self.startAtom_x_edit.setText(f"{nm_pos.x():.2f}")
            if self.atoms is None:
                if 'atoms' in self.parent.dataset.metadata.keys():
                    self.atoms = self.parent.dataset.metadata['atoms']['positions']
            if self.atoms is not None:
                self.start_atom = np.argmin(np.linalg.norm(self.atoms[:,:2] - np.array([pos.x(), pos.y()]), axis=1))
                self.parent.status.showMessage(f'Atom {self.start_atom} at {nm_pos.x():.2f}nm, {nm_pos.y():.2f}nm')        
    def copy_atoms_to(self):
        pass
        
    def find_atoms(self,  value=0):
        atom_size = float(self.atomSize_edit.displayText())
        threshold = float(self.atomThreshold_edit.displayText())
        if hasattr(self.parent.dataset, 'x'):
            scale = self.parent.dataset.x[1]-self.parent.dataset.x[0]
        else:
            scale = 1.
        self.parent.status.showMessage('Finding Atoms')
        image = np.array(self.parent.dataset)
        image -= image.min()
        image /= image.max()
        self.atoms = pyTEMlib.atom_tools.find_atoms(image, atom_size=atom_size/scale, threshold=threshold)
        if 'atoms' not in self.parent.dataset.metadata.keys():
            self.parent.dataset.metadata['atoms'] = {}     
        self.parent.status.showMessage(f'Found {len(self.atoms)} Atoms')
        self.parent.dataset.metadata['atoms']['positions'] = self.atoms
        self.parent.dataset.metadata['atoms']['size'] = atom_size
        self.parent.dataset.metadata['plot']['additional_features'] = 'Image'
        self.atoms_A = self.atoms *scale*10
        self.parent.plotUpdate()
        self.atomsButton.setChecked(False)
        
    def set_structure(self):
        crystal_name = self.structureList.currentText()
        self.crystal = pyTEMlib.crystal_tools.structure_by_name(crystal_name)
        print(crystal_name)
        
    def graph_hopp(self):
        
        self.set_structure()
        hkl = self.zoneAxis_edit.displayText()
        try:
            hkl = np.array([int(i) for i in hkl.split()])
        except:
            hkl = np.array([int(i) for i in hkl.split(',')])
        pos_x = float(self.startAtom_x_edit.displayText())
        pos_y = float(self.startAtom_y_edit.displayText())
        self.start_atom = np.argmin(np.linalg.norm(self.atoms[:,:2] - np.array([pos_x, pos_y]), axis=1))
                
        self.crystal.info['experimental']={'zone_axis': hkl, 'angle': 0}
        lattice_parameter = self.crystal.cell.lengths()[:2]/10/self.parent.dataset.x.slope
        print(lattice_parameter)
        hopped, out = pyTEMlib.graph_tools.breadth_first_search_felxible(self.atoms[:,:2], self.start_atom, lattice_parameter)
        self.parent.status.showMessage(f'Found {len(hopped)} Atoms')
        angles = hopped[:,2]   
        print(np.unique(np.int16(np.mod(np.round(angles,0), self.crystal.cell.angles()[2])+0.5)))
        # print(out)
        
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
            self.atoms_A = np.array(pos)*10
        return plot_features   


def breadth_first_search(graph, initial, layer, accuracy=3, Z_contrast=True):
    sane_crystal = False
    if isinstance(layer, ase.Atoms):
        if 'experimental' in layer.info:
            if 'zone_axis' in layer.info['experimental']:
                sane_crystal = True
            if 'angle' not in layer.info['experimental']:
                layer.info['experimental']['angle'] = 0.
    if not sane_crystal:
        raise ValueError('Reference crystal tructure is not of type ase.Atoms or does not contain a zone axis to project')
    layer = pyTEMlib.crystal_tools.get_projection(layer)
    if Z_contrast:
        del layer[(layer.get_atomic_numbers() < layer.get_atomic_numbers().max()/2)]
    tree = scipy.spatial.cKDTree(layer.positions[:,:2])
    distances, indices = tree.query(layer.positions[:,:2], 5)
    distances[np.isinf(distances)] = 0
    if accuracy < 1:
        deviation = accuracy
    else:
        deviation1 = np.abs(layer.cell.lengths()[0] - np.unique(distances)).min()
        deviation2 = np.abs(layer.cell.lengths()[1] - np.unique(distances)).min()
        deviation = np.min([deviation1, deviation2])/2
    hop_distance = np.unique(layer.cell.lengths()[:2])
    neighbour_tree = scipy.spatial.KDTree(graph)
    coordination_matrix = np.zeros([len(graph), len(graph)])
    visited = []  # the atoms we visited
    queue = [initial]
    angle = []  # orientation of unit cell
    distances, indices = neighbour_tree.query(graph,k=20)  
    while queue:
        node = queue.pop(0)
        if node not in visited:
            visited.append(node)
            neighbors = indices[node]
            for neighbour in neighbors:  
                if neighbour not in visited and neighbour < len(graph):
                    distance = np.linalg.norm(graph[node] - graph[neighbour])
                    
                    distance_to_ideal = np.abs(hop_distance - distance)
                    print(node, neighbour, distance , distance_to_ideal, deviation)
                    if np.min(distance_to_ideal) < deviation:
                        angle.append(np.degrees(np.arctan2((graph[node] - graph[neighbour])[1], (graph[node] - graph[neighbour])[0])))
                        queue.append(neighbour)   
                        coordination_matrix[node, neighbour] = distance
                        coordination_matrix[neighbour, node] = distance
    output = {'reference': layer, 'visited': visited, 'angle': angle,
              'coordination_matrix': coordination_matrix,
              'accuracy': deviation}
    return visited, angle, output              

    