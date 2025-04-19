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

class ProbeDialog(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ProbeDialog, self).__init__(parent)
    
        self.parent = parent
        self.aberrations = {'C10': 0, 'C12a': 0, 'C12b': 0.38448128113770325,
                            'C21a': -68.45251255685642, 'C21b': 64.85359774641199, 'C23a': 11.667578600494137,
                            'C23b': -29.775627778458194,
                            'C30': 123,
                            'C32a': 95.3047364258614, 'C32b': -189.72105710231244, 'C34a': -47.45099594807912,
                            'C34b': -94.67424667529909,
                            'C41a': -905.31842572806, 'C41b': 981.316128853203, 'C43a': 4021.8433526960034,
                            'C43b': 131.72716642732158,
                            'C45a': -4702.390968272048, 'C45b': -208.25028574642903, 'C50': 552000., 'C52a': 0.,
                            'C52b': 0.,
                            'C54a': 0., 'C54b': 0., 'C56a': -36663.643489934424, 'C56b': 21356.079837905396,
                            'Cc': 0, 'dE': 0}

        layout = self.get_sidbar()
        self.atoms = None
        self.setLayout(layout)    
        self.name = 'Probe'
        self.setWindowTitle(self.name)



    def get_sidbar(self):
        validfloat = QtGui.QDoubleValidator()
        
        layout = QtWidgets.QGridLayout()
        row = 0
        self.mainList = QtWidgets.QComboBox(self)
        self.mainList.addItems(['None', 'Microscope', 'Spectra300', 'Zeiss200', 'Nion US200', 'Nion US100'])
        layout.addWidget(self.mainList,  row,0, 1, 4)
        layout.setColumnStretch(0, 4)

        # self.mainList.activated[str].connect(self.update_image_dataset)
        
        row += 1
        self.regButton = QtWidgets.QPushButton()
        self.regButton.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.regButton.setText("Aberrations")
        layout.addWidget(self.regButton,  row,0, 1, 4)
        layout.setColumnStretch(0, 3) 
        #self.scaleButton.clicked.connect(self.rigi_registration)

        row+= 1
        radiobutton = QtWidgets.QRadioButton("Nion")
        radiobutton.setChecked(True)
        radiobutton.convention = "Nion"
        #radiobutton.toggled.connect(self.onClicked)
        layout.addWidget(radiobutton, 0, 0)

        radiobutton = QtWidgets.QRadioButton("Ceos")
        radiobutton.convention = "Ceos"
        #radiobutton.toggled.connect(self.onClicked)
        layout.addWidget(radiobutton, 0, 1)

        row += 1
        i = 0
        self.aEdit = []
        for key in self.aberrations:
            self.aLabel = QtWidgets.QLabel(key)
            self.aEdit.append(QtWidgets.QLineEdit(f"{self.aberrations[key]:.1f}"))
            self.aEdit[i].setValidator(validfloat)
            self.aEdit[i].uniqueId = i + 55555
            self.aEdit[i].editingFinished.connect(self.OnAberrEnter)
            self.aUnit = QtWidgets.QLabel("nm")
            if key[-1] == 'b':
                layout.addWidget(self.aLabel, row, 2)
                layout.addWidget(self.aEdit[i], row, 3)
                # layout.addWidget(self.aUnit,row,2)
            elif key[-1] == 'E':
                layout.addWidget(self.aLabel, row, 2)
                layout.addWidget(self.aEdit[i], row, 3)
            else:
                row += 1
                layout.addWidget(self.aLabel, row, 0)
                layout.addWidget(self.aEdit[i], row, 1)
                # layout.addWidget(self.aUnit,row,2)
            i += 1
        self.aEdit[0].setFocus()

        row += 1
        self.clusterButton = QtWidgets.QPushButton()
        self.clusterButton.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.clusterButton.setText("Process")
        layout.addWidget(self.clusterButton, row, 0, 1, 4)
        layout.setColumnStretch(0, 3)
        row += 1

        self.process = ['Gauss Probe', 'Real Probe', 'Ronchigram']

        self.processList = QtWidgets.QComboBox()
        self.processList.setEditable(False)
        self.processList.addItems(self.process)
        self.processList.activated[str].connect(self.onProcessSelect)

        layout.addWidget(self.processList, row, 1)
        # layout.addWidget(self.TEMLabel, row, 0)


        row += 1
        self.clusterButton =  QtWidgets.QPushButton()
        self.clusterButton.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.clusterButton.setText("Cluster Tools")
        layout.addWidget(self.clusterButton,  row,0, 1, 3)
        layout.setColumnStretch(0, 3) 
        # self.scaleButton.clicked.connect(self.cursor2energy_scale)

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

    def onProcessSelect(self, text):
        eNum = self.processList.currentIndex()
        # print(eNum)
        if self.process[eNum] == 'Gauss Probe':
            pass

            #Gauss_width = (qf['resolution'] / qf['pixel_size']) * 2.35482
            #probe = self.parent.ImageDialog.MakeProbeG(qf['image'].shape[0], Gauss_width)
            #self.parent.text2.append('\n Making Gaussian Probe with resolution  ' + str(qf['resolution']) + 'nm')



        if self.process[eNum] == 'Real Probe':
            pass

        if self.process[eNum] == 'Default Aber.':
            pass
            #self.probe.DefaultAberrations()



    def OnAberrEnter(self):
        edit = self.sender()
        uid = edit.uniqueId - 55555
        key = self.aberrations[uid]

        whichImage = self.parent.tags['images']['current']
        tags = {'Aberrations': {}}
        tags['Aberrations'][key] = float(edit.displayText().strip())
        # print (key, tags['Aberrations'][key])

        # self.update()

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
        
        self.atoms = pyTEMlib.atom_tools.find_atoms(self.parent.dataset, atom_size=atom_size, threshold=threshold)
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

    