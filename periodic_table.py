from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import numpy as np

class PeriodicTable(QDialog):# standard periodic table elements (q symbolizes an empty space)
        def __init__(self, parent=None):
            super(QWidget, self).__init__(parent)
            self.parent = parent
            self.elements_selected = []
            
            #  * --> Lanthanides
            # ** --> Actinides
            # 18 items per line
            pt1 = """H,q,q,q,q,q,q,q,q,q,q,q,q,q,q,q,q,
He,Li,Be,q,q,q,q,q,q,q,q,q,q,B,C,N,O,F,Ne,\
Na,Mg,q,q,q,q,q,q,q,q,q,q,Al,Si,P,S,Cl,Ar,\
K,Ca,Sc,Ti,V,Cr,Mn,Fe,Co,Ni,Cu,Zn,Ga,Ge,As,Se,Br,Kr,
Rb,Sr,Y,Zr,Nb,Mo,Tc,Ru,Rh,Pd,Ag,Cd,In,Sn,Sb,Te,I,Xe,
Cs,Ba,*,Hf,Ta,W,Re,Os,Ir,Pt,Au,Hg,Ti,Pb,Bi,Po,At,Rn,
Fr,Ra,**,Rf,Db,Sg,Bh,Hs,Mt,Ds,Rg,q,q,q,q,q,q,q"""

            # Lanthanides and Actinides ...
            # 15 items per line
            pt2 = """ ,*,La,Ce,Pr,Nd,Pm,Sm,Eu,Gd,Tb,Dy,Ho,Er,Tm,Yb,Lu,
 ,**,Ac,Th,Pa,U,Np,Pu,Am,Cm,Bk,Cf,Es,Fm,Md,No,Lr"""

            # convert standard periodic table elements into a list
            list_pt1 = pt1.replace('\n', "").replace('q', " ").split(",")

            # convert Lanthanides and Actinides into a list
            list_pt2 = pt2.replace('\n', "").split(",")

            self.element_dict = \
            {'Ru': 'Ruthenium', 'Re': 'Rhenium', 'Ra': 'Radium', 'Rb': 'Rubidium',
            'Rn': 'Radon', 'Rh': 'Rhodium', 'Be': 'Beryllium', 'Ba': 'Barium',
            'Bi': 'Bismuth', 'Br': 'Bromine', 'H': 'Hydrogen', 'P': 'Phosphorus',
            'Os': 'Osmium', 'Hg': 'Mercury', 'Ge': 'Germanium', 'Gd': 'Gadolinium',
            'Ga': 'Gallium', 'Pr': 'Praseodymium', 'Pt': 'Platinum',
            'Pu': 'Plutonium', 'C': 'Carbon', 'Pb': 'Lead ', 'Pa': 'Proctactinium',
            'Pd': 'Palladium', 'Cd': 'Cadmium', 'Po': 'Polonium', 'Pm': 'Promethium',
            'Ho': 'Holmium', 'Hf': 'Hafnium', 'K': 'Potassium', 'He': 'Helium',
            'Mg': 'Magnesium', 'Mo': 'Molybdenum', 'Mn': 'Manganese', 'O': 'Oxygen',
            'S': 'Sulfur', 'W': 'Tungsten', 'Zn': 'Zinc', 'Eu': 'Europium',
            'Zr': 'Zirconium', 'Er': 'Erbium', 'Ni': 'Nickel', 'Na': 'Sodium',
            'Nb': 'Niobium', 'Nd': 'Neodymium', 'Ne': 'Neon', 'Np': 'Neptunium',
            'Fr': 'Francium', 'Fe': 'Iron', 'B': 'Boron', 'F': 'Fluorine',
            'Sr': 'Strontium', 'N': 'Nitrogen', 'Kr': 'Krypton', 'Si': 'Silicon',
            'Sn': 'Tin', 'Sm': 'Samarium', 'V': 'Vanadium', 'Sc': 'Scandium',
            'Sb': 'Antimony', 'Se': 'Selenium', 'Co': 'Cobalt', 'Cl': 'Chlorine',
            'Ca': 'Calcium ', 'Ce': 'Cerium', 'Xe': 'Xenon', 'Lu': 'Lutetium',
            'Cs': 'Cesium', 'Cr': 'Chromium', 'Cu': 'Copper', 'La': 'Lanthanum',
            'Li': 'Lithium', 'Tl': 'Thallium', 'Tm': 'Thulium', 'Th': 'Thorium',
            'Ti': 'Titanium', 'Te': 'Tellurium', 'Tb': 'Terbium', 'Tc': 'Technetium',
            'Ta': 'Tantalum', 'Yb': 'Ytterbium', 'Dy': 'Dysprosium', 'I': 'Iodine',
            'U': 'Uranium', 'Y': 'Yttrium', 'Ac': 'Actinium', 'Ag': 'Silver',
            'Ir': 'Iridium', 'Am': 'Americium', 'Al': 'Aluminum', 'As': 'Arsenic',
            'Ar': 'Argon', 'Au': 'Gold', 'At': 'Astatine', 'In': 'Indium'}


            #GD self.SetBackgroundColour('green')
            


            vsizer = QVBoxLayout()
            # use grid layout
            gsizer = QGridLayout()

            MainGroup = QWidget()
            

            #GD:font = wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD)
            self.buttons1 = []
            index = 0
            self.button = []
            color = "background-color: lightblue;\n"
            for i in range(7):
                for j in range(18):
                    symbol =list_pt1[index]
                    self.button.append(QPushButton(symbol))

                    if symbol == 'Al':
                        color = "background-color: lightgreen;\n"
                    if symbol == 'Se':
                        color = "background-color: red;\n"
                    
                    self.button[index].setStyleSheet(color)
                    
                    self.button[index].setFixedWidth(25)
                    self.button[index].setCheckable(1)
                    
                    #GD:self.buttons1[ix].SetFont(font)

                    if symbol != ' ':
                        gsizer.addWidget(self.button[index],i,j)
                    index+=1
            MainGroup.setLayout(gsizer) 
            
            # sizer for Lanthanides and Actinides
            gsizer2 = QGridLayout()
            offset = index
            for i in range(2):
                for j in range(17):
                    symbol =list_pt2[index-offset]
                    self.button.append(QPushButton(symbol))
                    color = "background-color: pink;\n"
                    
                    self.button[index].setStyleSheet(color)
                    
                    self.button[index].setFixedWidth(25)
                    self.button[index].setCheckable(1)
                    
                    #self.buttons2[ix].SetFont(font)

                    if symbol != ' ':
                        gsizer2.addWidget(self.button[index],i,j)
                    index+=1

            LaAc = QWidget()
            LaAc.setLayout(gsizer2) 
            
            vsizer.addWidget(MainGroup)
            vsizer.addWidget(LaAc)
            
            self.setLayout(vsizer)

            OKButton  = QPushButton('OK')
            OKButton.clicked.connect(self.OnClose)
        
            vsizer.addWidget(OKButton)
            self.setLayout(vsizer)
            self.setModal(True)
            # self.show()

        def OnClose(self):
            self.elements_selected = []
            for btn in self.button:
                if btn.isChecked():
                    if btn.text() in self.element_dict:
                        self.elements_selected.append(btn.text())
            # self.elements_selected = self.parent.elements_selected#.copy()
            self.accept()
            
