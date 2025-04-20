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

import sys
sys.path.insert(0,'/lustre/isaac24/proj/UTK0286/STEM_TF/Autoscript/autoscript_code_lib/')
acquistion_enabled = True
try:
    from autoscript_tem_microscope_client import TemMicroscopeClient
    from autoscript_tem_microscope_client.enumerations import *
    from autoscript_tem_microscope_client.structures import *
except:
    acquistion_enabled = False

import numpy as np
import sidpy
import scipy
import ase

from pyTEMlib import image_tools
import pyTEMlib.atom_tools
import pyTEMlib.crystal_tools
import pyTEMlib.graph_tools


class MicroscopeDialog(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MicroscopeDialog, self).__init__(parent)
    
        self.parent = parent
        layout = self.get_sidbar()
        self.atoms = None
        self.setLayout(layout)    
        self.name = 'Mic'
        if acquistion_enabled:
            self.microscope = TemMicroscopeClient()
            self.parent.microscope = self.microscope
        else:
            self.parent.microscope = None
        self.setWindowTitle(self.name)
        
    def get_sidbar(self): 
        validfloat = QtGui.QDoubleValidator()

        row += 1
        self.connectButton = QtWidgets.QPushButton()
        self.connectButton.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.connectButton.setText("Connect to Microsopcope")
        self.connectButton.setCheckable(True)
        self.connectButton.setChecked(False)
        layout.addWidget(self.connectButton, row, 0, 1, 3)
        layout.setColumnStretch(0, 3)
        self.connectButton.clicked.connect(self.connect)

        row += 1
        self.ipLabel = QtWidgets.QLabel("IP Address")
        self.ipEdit = QtWidgets.QLineEdit("10.46.217.242")
        layout.addWidget(self.ipLabel, row, 0)
        layout.addWidget(self.ipEdit, row, 1)

        row += 1
        self.portLabel = QtWidgets.QLabel("Port")
        self.portEdit = QtWidgets.QLineEdit("9090")
        layout.addWidget(self.portLabel, row, 0)
        layout.addWidget(self.portEdit, row, 1)

        
        layout = QtWidgets.QGridLayout()
        row = 0
        self.vacuum_label = QtWidgets.QLabel("Vacuum")
        layout.addWidget(self.vacuum_label, row, 0)
        self.vacuum_edit = QtWidgets.QLineEdit("Not Ready")
        layout.addWidget(self.vacuum_edit, row, 1)
        self.valveButton = QtWidgets.QPushButton()
        self.valveButton.setText("Column valve")
        self.valveButton.setCheckable(True)
        layout.addWidget(self.valveButton, row, 2)
        # self.hoppButton.clicked.connect(self.valveButton)

        # self.mainList.activated[str].connect(self.update_image_dataset)
        
        row += 1
        self.opticButton = QtWidgets.QPushButton()
        self.opticButton.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.opticButton.setText("Optics")
        layout.addWidget(self.opticButton,  row,0, 1, 3)
        layout.setColumnStretch(0, 3) 
        #self.scaleButton.clicked.connect(self.rigi_registration)
        row += 1
        radiobutton = QtWidgets.QRadioButton("TEM")
        radiobutton.setChecked(True)
        radiobutton.convention = "TEM"
        # radiobutton.toggled.connect(self.onClicked)
        layout.addWidget(radiobutton, row, 1)

        radiobutton = QtWidgets.QRadioButton("STEM")
        radiobutton.convention = "STEM"
        # radiobutton.toggled.connect(self.onClicked)
        layout.addWidget(radiobutton, row, 2)
        radiobutton = QtWidgets.QRadioButton("Diff")
        radiobutton.convention = "Diff"
        # radiobutton.toggled.connect(self.onClicked)
        layout.addWidget(radiobutton, row, 1)

        row += 1
        self.focus_label = QtWidgets.QLabel("Focus")
        self.focus_edit = QtWidgets.QDoubleSpinBox()
        self.focus_edit.setMinimum(-5000)
        self.focus_edit.setMaximum(5000)
        self.focus_edit.setSingleStep(4)
        self.focus_unit = QtWidgets.QLabel("nm")
        layout.addWidget(self.focus_label, row, 0)
        layout.addWidget(self.focus_edit, row, 1)
        layout.addWidget(self.focus_unit, row, 2)

        row += 1
        self.c1a1Button = QtWidgets.QPushButton()
        self.c1a1Button.setText("C1/A1")
        layout.addWidget(self.c1a1Button, row, 0)

        self.b2Button = QtWidgets.QPushButton()
        self.b2Button.setText("B2")
        layout.addWidget(self.b2Button, row, 1)

        self.a2Button = QtWidgets.QPushButton()
        self.a2Button.setText("A2")
        layout.addWidget(self.a2Button, row, 2)


        row += 1
        self.magnification_label = QtWidgets.QLabel("Magnification")
        self.magnification_edit = QtWidgets.QLineEdit("0.1")
        self.magnification_edit.setValidator(validfloat)
        self.magnification_unit = QtWidgets.QLabel("nm")
        layout.addWidget(self.magnification_label, row, 0)
        layout.addWidget(self.magnification_edit, row, 1)
        layout.addWidget(self.magnification_unit, row, 2)

        row += 1
        self.convergence_label = QtWidgets.QLabel("Convergence")
        self.convergence_edit = QtWidgets.QLineEdit("30")
        self.convergence_edit.setValidator(validfloat)
        self.convergence_unit = QtWidgets.QLabel("mrad")
        layout.addWidget(self.convergence_label, row, 0)
        layout.addWidget(self.convergence_edit, row, 1)
        layout.addWidget(self.convergence_unit, row, 2)
        
        row += 1
        self.opticButton = QtWidgets.QPushButton()
        self.opticButton.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.opticButton.setText("Stage")
        layout.addWidget(self.opticButton, row, 0, 1, 3)
        layout.setColumnStretch(0, 3)

        row += 1
        self.stage_x_label = QtWidgets.QLabel("x")
        self.stage_x_edit = QtWidgets.QDoubleSpinBox()
        self.stage_x_edit.setMinimum(-1500000)
        self.stage_x_edit.setMaximum( 1500000)
        self.stage_x_edit.setSingleStep(10)
        self.stage_x_unit = QtWidgets.QLabel("nm")
        layout.addWidget(self.stage_x_label, row, 0)
        layout.addWidget(self.stage_x_edit, row, 1)
        layout.addWidget(self.stage_x_unit, row, 2)

        row += 1
        self.stage_y_label = QtWidgets.QLabel("y")
        self.stage_y_edit = QtWidgets.QDoubleSpinBox()
        self.stage_y_edit.setMinimum(-1500000)
        self.stage_y_edit.setMaximum( 1500000)
        self.stage_y_edit.setSingleStep(10)
        self.stage_y_unit = QtWidgets.QLabel("nm")
        layout.addWidget(self.stage_y_label, row, 0)
        layout.addWidget(self.stage_y_edit, row, 1)
        layout.addWidget(self.stage_y_unit, row, 2)

        row += 1
        self.stage_z_label = QtWidgets.QLabel("z")
        self.stage_z_edit = QtWidgets.QDoubleSpinBox()
        self.stage_z_edit.setMinimum(-500000)
        self.stage_z_edit.setMaximum( 500000)
        self.stage_z_edit.setSingleStep(10)
        self.stage_z_unit = QtWidgets.QLabel("nm")
        layout.addWidget(self.stage_z_label, row, 0)
        layout.addWidget(self.stage_z_edit, row, 1)
        layout.addWidget(self.stage_z_unit, row, 2)

        row += 1
        self.stage_a_label = QtWidgets.QLabel("alpha")
        self.stage_a_edit = QtWidgets.QDoubleSpinBox()
        self.stage_a_edit.setMinimum(-15)
        self.stage_a_edit.setMaximum( 15)
        self.stage_a_edit.setSingleStep(.1)
        self.stage_a_unit = QtWidgets.QLabel("deg")
        layout.addWidget(self.stage_a_label, row, 0)
        layout.addWidget(self.stage_a_edit, row, 1)
        layout.addWidget(self.stage_a_unit, row, 2)

        row += 1
        self.stage_b_label = QtWidgets.QLabel("beta")
        self.stage_b_edit = QtWidgets.QDoubleSpinBox()
        self.stage_b_edit.setMinimum(-15)
        self.stage_b_edit.setMaximum( 15)
        self.stage_b_edit.setSingleStep(.1)
        self.stage_b_unit = QtWidgets.QLabel("deg")
        layout.addWidget(self.stage_b_label, row, 0)
        layout.addWidget(self.stage_b_edit, row, 1)
        layout.addWidget(self.stage_b_unit, row, 2)


        
        return layout

    def connect(self):
        """
        Connect with autoscript to microscope
        """
        ip = self.ipEdit.displayText()
        if self.connectButton.isChecked():
            port = int(self.portEdit.displayText())
            self.microscope.connect(ip, port=port)
            self.connectButton.setText(f"Connected: {}self.microscope.system.name}")
        else:
            self.connectButton.setText(f"Microscope")
            self.microscope.disconnect()

    def update_sidebar(self):
        if '_relationship' not in self.parent.datasets:
            return
        image_list = ['None']
        image_index = 0

        # if self.parent.microscope is not None:

        """if microscope.vacuum.state == "Ready":
     microscope.vacuum.column_valves.open()
     print("open")
print(microscope.vacuum.column_valves.state)
axes = ['x', 'y', 'z', 'a', 'b']
print(microscope.specimen.stage.position.x)
print(microscope.specimen.stage.get_holder_type())
for axis in axes:
    print(microscope.specimen.stage.get_axis_limits(axis).min)
    print(microscope.specimen.stage.get_axis_limits(axis).max)
microscope.optics.monochromator.focus = -50
print(microscope.optics.monochromator.focus)
print(microscope.optics.monochromator.shift)
print(microscope.optics.magnification.available_values)
print(microscope.optics.magnification.value)

relative_move(self, relative_position: 'Union[StagePosition, list, tuple]')
 |      Moves the stage relatively to the current stage position.
 absolute_move(self, position: 'Union[StagePosition, list, tuple]')
 |      Moves the stage to a new position.
 
 
 microscope.optics.optical_mode = 'Tem'
microscope.optics.focus = 50*1e-9
print(microscope.optics.focus)
microscope.optics.optical_mode, microscope.optics.probe_mode, microscope.optics.spot_size_index
    """

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

    