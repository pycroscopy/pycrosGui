"""
Modern Periodic Table Dialog
Part of pycrosGUI - pycroscopy ecosystem

Features:
- All 118 elements with proper positioning
- Category-based coloring
- Element information display
- Modern flat design
"""
try:
    from PyQt6 import QtWidgets, QtCore, QtGui
    from PyQt6.QtCore import Qt
except ImportError:
    from PyQt5 import QtWidgets, QtCore, QtGui
    from PyQt5.QtCore import Qt


# Complete element data with categories
ELEMENTS = {
    # Period 1
    'H': {'name': 'Hydrogen', 'number': 1, 'mass': 1.008, 'category': 'nonmetal', 'row': 0, 'col': 0},
    'He': {'name': 'Helium', 'number': 2, 'mass': 4.003, 'category': 'noble_gas', 'row': 0, 'col': 17},
    # Period 2
    'Li': {'name': 'Lithium', 'number': 3, 'mass': 6.94, 'category': 'alkali_metal', 'row': 1, 'col': 0},
    'Be': {'name': 'Beryllium', 'number': 4, 'mass': 9.012, 'category': 'alkaline_earth', 'row': 1, 'col': 1},
    'B': {'name': 'Boron', 'number': 5, 'mass': 10.81, 'category': 'metalloid', 'row': 1, 'col': 12},
    'C': {'name': 'Carbon', 'number': 6, 'mass': 12.011, 'category': 'nonmetal', 'row': 1, 'col': 13},
    'N': {'name': 'Nitrogen', 'number': 7, 'mass': 14.007, 'category': 'nonmetal', 'row': 1, 'col': 14},
    'O': {'name': 'Oxygen', 'number': 8, 'mass': 15.999, 'category': 'nonmetal', 'row': 1, 'col': 15},
    'F': {'name': 'Fluorine', 'number': 9, 'mass': 18.998, 'category': 'halogen', 'row': 1, 'col': 16},
    'Ne': {'name': 'Neon', 'number': 10, 'mass': 20.180, 'category': 'noble_gas', 'row': 1, 'col': 17},
    # Period 3
    'Na': {'name': 'Sodium', 'number': 11, 'mass': 22.990, 'category': 'alkali_metal', 'row': 2, 'col': 0},
    'Mg': {'name': 'Magnesium', 'number': 12, 'mass': 24.305, 'category': 'alkaline_earth', 'row': 2, 'col': 1},
    'Al': {'name': 'Aluminum', 'number': 13, 'mass': 26.982, 'category': 'post_transition', 'row': 2, 'col': 12},
    'Si': {'name': 'Silicon', 'number': 14, 'mass': 28.085, 'category': 'metalloid', 'row': 2, 'col': 13},
    'P': {'name': 'Phosphorus', 'number': 15, 'mass': 30.974, 'category': 'nonmetal', 'row': 2, 'col': 14},
    'S': {'name': 'Sulfur', 'number': 16, 'mass': 32.06, 'category': 'nonmetal', 'row': 2, 'col': 15},
    'Cl': {'name': 'Chlorine', 'number': 17, 'mass': 35.45, 'category': 'halogen', 'row': 2, 'col': 16},
    'Ar': {'name': 'Argon', 'number': 18, 'mass': 39.948, 'category': 'noble_gas', 'row': 2, 'col': 17},
    # Period 4
    'K': {'name': 'Potassium', 'number': 19, 'mass': 39.098, 'category': 'alkali_metal', 'row': 3, 'col': 0},
    'Ca': {'name': 'Calcium', 'number': 20, 'mass': 40.078, 'category': 'alkaline_earth', 'row': 3, 'col': 1},
    'Sc': {'name': 'Scandium', 'number': 21, 'mass': 44.956, 'category': 'transition_metal', 'row': 3, 'col': 2},
    'Ti': {'name': 'Titanium', 'number': 22, 'mass': 47.867, 'category': 'transition_metal', 'row': 3, 'col': 3},
    'V': {'name': 'Vanadium', 'number': 23, 'mass': 50.942, 'category': 'transition_metal', 'row': 3, 'col': 4},
    'Cr': {'name': 'Chromium', 'number': 24, 'mass': 51.996, 'category': 'transition_metal', 'row': 3, 'col': 5},
    'Mn': {'name': 'Manganese', 'number': 25, 'mass': 54.938, 'category': 'transition_metal', 'row': 3, 'col': 6},
    'Fe': {'name': 'Iron', 'number': 26, 'mass': 55.845, 'category': 'transition_metal', 'row': 3, 'col': 7},
    'Co': {'name': 'Cobalt', 'number': 27, 'mass': 58.933, 'category': 'transition_metal', 'row': 3, 'col': 8},
    'Ni': {'name': 'Nickel', 'number': 28, 'mass': 58.693, 'category': 'transition_metal', 'row': 3, 'col': 9},
    'Cu': {'name': 'Copper', 'number': 29, 'mass': 63.546, 'category': 'transition_metal', 'row': 3, 'col': 10},
    'Zn': {'name': 'Zinc', 'number': 30, 'mass': 65.38, 'category': 'transition_metal', 'row': 3, 'col': 11},
    'Ga': {'name': 'Gallium', 'number': 31, 'mass': 69.723, 'category': 'post_transition', 'row': 3, 'col': 12},
    'Ge': {'name': 'Germanium', 'number': 32, 'mass': 72.630, 'category': 'metalloid', 'row': 3, 'col': 13},
    'As': {'name': 'Arsenic', 'number': 33, 'mass': 74.922, 'category': 'metalloid', 'row': 3, 'col': 14},
    'Se': {'name': 'Selenium', 'number': 34, 'mass': 78.971, 'category': 'nonmetal', 'row': 3, 'col': 15},
    'Br': {'name': 'Bromine', 'number': 35, 'mass': 79.904, 'category': 'halogen', 'row': 3, 'col': 16},
    'Kr': {'name': 'Krypton', 'number': 36, 'mass': 83.798, 'category': 'noble_gas', 'row': 3, 'col': 17},
    # Period 5
    'Rb': {'name': 'Rubidium', 'number': 37, 'mass': 85.468, 'category': 'alkali_metal', 'row': 4, 'col': 0},
    'Sr': {'name': 'Strontium', 'number': 38, 'mass': 87.62, 'category': 'alkaline_earth', 'row': 4, 'col': 1},
    'Y': {'name': 'Yttrium', 'number': 39, 'mass': 88.906, 'category': 'transition_metal', 'row': 4, 'col': 2},
    'Zr': {'name': 'Zirconium', 'number': 40, 'mass': 91.224, 'category': 'transition_metal', 'row': 4, 'col': 3},
    'Nb': {'name': 'Niobium', 'number': 41, 'mass': 92.906, 'category': 'transition_metal', 'row': 4, 'col': 4},
    'Mo': {'name': 'Molybdenum', 'number': 42, 'mass': 95.95, 'category': 'transition_metal', 'row': 4, 'col': 5},
    'Tc': {'name': 'Technetium', 'number': 43, 'mass': 98, 'category': 'transition_metal', 'row': 4, 'col': 6},
    'Ru': {'name': 'Ruthenium', 'number': 44, 'mass': 101.07, 'category': 'transition_metal', 'row': 4, 'col': 7},
    'Rh': {'name': 'Rhodium', 'number': 45, 'mass': 102.91, 'category': 'transition_metal', 'row': 4, 'col': 8},
    'Pd': {'name': 'Palladium', 'number': 46, 'mass': 106.42, 'category': 'transition_metal', 'row': 4, 'col': 9},
    'Ag': {'name': 'Silver', 'number': 47, 'mass': 107.87, 'category': 'transition_metal', 'row': 4, 'col': 10},
    'Cd': {'name': 'Cadmium', 'number': 48, 'mass': 112.41, 'category': 'transition_metal', 'row': 4, 'col': 11},
    'In': {'name': 'Indium', 'number': 49, 'mass': 114.82, 'category': 'post_transition', 'row': 4, 'col': 12},
    'Sn': {'name': 'Tin', 'number': 50, 'mass': 118.71, 'category': 'post_transition', 'row': 4, 'col': 13},
    'Sb': {'name': 'Antimony', 'number': 51, 'mass': 121.76, 'category': 'metalloid', 'row': 4, 'col': 14},
    'Te': {'name': 'Tellurium', 'number': 52, 'mass': 127.60, 'category': 'metalloid', 'row': 4, 'col': 15},
    'I': {'name': 'Iodine', 'number': 53, 'mass': 126.90, 'category': 'halogen', 'row': 4, 'col': 16},
    'Xe': {'name': 'Xenon', 'number': 54, 'mass': 131.29, 'category': 'noble_gas', 'row': 4, 'col': 17},
    # Period 6
    'Cs': {'name': 'Cesium', 'number': 55, 'mass': 132.91, 'category': 'alkali_metal', 'row': 5, 'col': 0},
    'Ba': {'name': 'Barium', 'number': 56, 'mass': 137.33, 'category': 'alkaline_earth', 'row': 5, 'col': 1},
    'Hf': {'name': 'Hafnium', 'number': 72, 'mass': 178.49, 'category': 'transition_metal', 'row': 5, 'col': 3},
    'Ta': {'name': 'Tantalum', 'number': 73, 'mass': 180.95, 'category': 'transition_metal', 'row': 5, 'col': 4},
    'W': {'name': 'Tungsten', 'number': 74, 'mass': 183.84, 'category': 'transition_metal', 'row': 5, 'col': 5},
    'Re': {'name': 'Rhenium', 'number': 75, 'mass': 186.21, 'category': 'transition_metal', 'row': 5, 'col': 6},
    'Os': {'name': 'Osmium', 'number': 76, 'mass': 190.23, 'category': 'transition_metal', 'row': 5, 'col': 7},
    'Ir': {'name': 'Iridium', 'number': 77, 'mass': 192.22, 'category': 'transition_metal', 'row': 5, 'col': 8},
    'Pt': {'name': 'Platinum', 'number': 78, 'mass': 195.08, 'category': 'transition_metal', 'row': 5, 'col': 9},
    'Au': {'name': 'Gold', 'number': 79, 'mass': 196.97, 'category': 'transition_metal', 'row': 5, 'col': 10},
    'Hg': {'name': 'Mercury', 'number': 80, 'mass': 200.59, 'category': 'transition_metal', 'row': 5, 'col': 11},
    'Tl': {'name': 'Thallium', 'number': 81, 'mass': 204.38, 'category': 'post_transition', 'row': 5, 'col': 12},
    'Pb': {'name': 'Lead', 'number': 82, 'mass': 207.2, 'category': 'post_transition', 'row': 5, 'col': 13},
    'Bi': {'name': 'Bismuth', 'number': 83, 'mass': 208.98, 'category': 'post_transition', 'row': 5, 'col': 14},
    'Po': {'name': 'Polonium', 'number': 84, 'mass': 209, 'category': 'metalloid', 'row': 5, 'col': 15},
    'At': {'name': 'Astatine', 'number': 85, 'mass': 210, 'category': 'halogen', 'row': 5, 'col': 16},
    'Rn': {'name': 'Radon', 'number': 86, 'mass': 222, 'category': 'noble_gas', 'row': 5, 'col': 17},
    # Period 7
    'Fr': {'name': 'Francium', 'number': 87, 'mass': 223, 'category': 'alkali_metal', 'row': 6, 'col': 0},
    'Ra': {'name': 'Radium', 'number': 88, 'mass': 226, 'category': 'alkaline_earth', 'row': 6, 'col': 1},
    'Rf': {'name': 'Rutherfordium', 'number': 104, 'mass': 267, 'category': 'transition_metal', 'row': 6, 'col': 3},
    'Db': {'name': 'Dubnium', 'number': 105, 'mass': 270, 'category': 'transition_metal', 'row': 6, 'col': 4},
    'Sg': {'name': 'Seaborgium', 'number': 106, 'mass': 271, 'category': 'transition_metal', 'row': 6, 'col': 5},
    'Bh': {'name': 'Bohrium', 'number': 107, 'mass': 270, 'category': 'transition_metal', 'row': 6, 'col': 6},
    'Hs': {'name': 'Hassium', 'number': 108, 'mass': 277, 'category': 'transition_metal', 'row': 6, 'col': 7},
    'Mt': {'name': 'Meitnerium', 'number': 109, 'mass': 276, 'category': 'transition_metal', 'row': 6, 'col': 8},
    'Ds': {'name': 'Darmstadtium', 'number': 110, 'mass': 281, 'category': 'transition_metal', 'row': 6, 'col': 9},
    'Rg': {'name': 'Roentgenium', 'number': 111, 'mass': 280, 'category': 'transition_metal', 'row': 6, 'col': 10},
    'Cn': {'name': 'Copernicium', 'number': 112, 'mass': 285, 'category': 'transition_metal', 'row': 6, 'col': 11},
    'Nh': {'name': 'Nihonium', 'number': 113, 'mass': 284, 'category': 'post_transition', 'row': 6, 'col': 12},
    'Fl': {'name': 'Flerovium', 'number': 114, 'mass': 289, 'category': 'post_transition', 'row': 6, 'col': 13},
    'Mc': {'name': 'Moscovium', 'number': 115, 'mass': 288, 'category': 'post_transition', 'row': 6, 'col': 14},
    'Lv': {'name': 'Livermorium', 'number': 116, 'mass': 293, 'category': 'post_transition', 'row': 6, 'col': 15},
    'Ts': {'name': 'Tennessine', 'number': 117, 'mass': 294, 'category': 'halogen', 'row': 6, 'col': 16},
    'Og': {'name': 'Oganesson', 'number': 118, 'mass': 294, 'category': 'noble_gas', 'row': 6, 'col': 17},
    # Lanthanides (row 8 in display, below main table)
    'La': {'name': 'Lanthanum', 'number': 57, 'mass': 138.91, 'category': 'lanthanide', 'row': 8, 'col': 3},
    'Ce': {'name': 'Cerium', 'number': 58, 'mass': 140.12, 'category': 'lanthanide', 'row': 8, 'col': 4},
    'Pr': {'name': 'Praseodymium', 'number': 59, 'mass': 140.91, 'category': 'lanthanide', 'row': 8, 'col': 5},
    'Nd': {'name': 'Neodymium', 'number': 60, 'mass': 144.24, 'category': 'lanthanide', 'row': 8, 'col': 6},
    'Pm': {'name': 'Promethium', 'number': 61, 'mass': 145, 'category': 'lanthanide', 'row': 8, 'col': 7},
    'Sm': {'name': 'Samarium', 'number': 62, 'mass': 150.36, 'category': 'lanthanide', 'row': 8, 'col': 8},
    'Eu': {'name': 'Europium', 'number': 63, 'mass': 151.96, 'category': 'lanthanide', 'row': 8, 'col': 9},
    'Gd': {'name': 'Gadolinium', 'number': 64, 'mass': 157.25, 'category': 'lanthanide', 'row': 8, 'col': 10},
    'Tb': {'name': 'Terbium', 'number': 65, 'mass': 158.93, 'category': 'lanthanide', 'row': 8, 'col': 11},
    'Dy': {'name': 'Dysprosium', 'number': 66, 'mass': 162.50, 'category': 'lanthanide', 'row': 8, 'col': 12},
    'Ho': {'name': 'Holmium', 'number': 67, 'mass': 164.93, 'category': 'lanthanide', 'row': 8, 'col': 13},
    'Er': {'name': 'Erbium', 'number': 68, 'mass': 167.26, 'category': 'lanthanide', 'row': 8, 'col': 14},
    'Tm': {'name': 'Thulium', 'number': 69, 'mass': 168.93, 'category': 'lanthanide', 'row': 8, 'col': 15},
    'Yb': {'name': 'Ytterbium', 'number': 70, 'mass': 173.05, 'category': 'lanthanide', 'row': 8, 'col': 16},
    'Lu': {'name': 'Lutetium', 'number': 71, 'mass': 174.97, 'category': 'lanthanide', 'row': 8, 'col': 17},
    # Actinides (row 9 in display)
    'Ac': {'name': 'Actinium', 'number': 89, 'mass': 227, 'category': 'actinide', 'row': 9, 'col': 3},
    'Th': {'name': 'Thorium', 'number': 90, 'mass': 232.04, 'category': 'actinide', 'row': 9, 'col': 4},
    'Pa': {'name': 'Protactinium', 'number': 91, 'mass': 231.04, 'category': 'actinide', 'row': 9, 'col': 5},
    'U': {'name': 'Uranium', 'number': 92, 'mass': 238.03, 'category': 'actinide', 'row': 9, 'col': 6},
    'Np': {'name': 'Neptunium', 'number': 93, 'mass': 237, 'category': 'actinide', 'row': 9, 'col': 7},
    'Pu': {'name': 'Plutonium', 'number': 94, 'mass': 244, 'category': 'actinide', 'row': 9, 'col': 8},
    'Am': {'name': 'Americium', 'number': 95, 'mass': 243, 'category': 'actinide', 'row': 9, 'col': 9},
    'Cm': {'name': 'Curium', 'number': 96, 'mass': 247, 'category': 'actinide', 'row': 9, 'col': 10},
    'Bk': {'name': 'Berkelium', 'number': 97, 'mass': 247, 'category': 'actinide', 'row': 9, 'col': 11},
    'Cf': {'name': 'Californium', 'number': 98, 'mass': 251, 'category': 'actinide', 'row': 9, 'col': 12},
    'Es': {'name': 'Einsteinium', 'number': 99, 'mass': 252, 'category': 'actinide', 'row': 9, 'col': 13},
    'Fm': {'name': 'Fermium', 'number': 100, 'mass': 257, 'category': 'actinide', 'row': 9, 'col': 14},
    'Md': {'name': 'Mendelevium', 'number': 101, 'mass': 258, 'category': 'actinide', 'row': 9, 'col': 15},
    'No': {'name': 'Nobelium', 'number': 102, 'mass': 259, 'category': 'actinide', 'row': 9, 'col': 16},
    'Lr': {'name': 'Lawrencium', 'number': 103, 'mass': 262, 'category': 'actinide', 'row': 9, 'col': 17},
}

# Category colors (modern flat design)
CATEGORY_COLORS = {
    'alkali_metal': '#FF6B6B',      # Red
    'alkaline_earth': '#FFA94D',    # Orange
    'transition_metal': '#FFD93D',  # Yellow
    'post_transition': '#6BCB77',   # Green
    'metalloid': '#4ECDC4',         # Teal
    'nonmetal': '#45B7D1',          # Blue
    'halogen': '#96CEB4',           # Sage
    'noble_gas': '#DDA0DD',         # Plum
    'lanthanide': '#FF9FF3',        # Pink
    'actinide': '#C8A2C8',          # Lilac
}

CATEGORY_LABELS = {
    'alkali_metal': 'Alkali Metal',
    'alkaline_earth': 'Alkaline Earth',
    'transition_metal': 'Transition Metal',
    'post_transition': 'Post-Transition',
    'metalloid': 'Metalloid',
    'nonmetal': 'Nonmetal',
    'halogen': 'Halogen',
    'noble_gas': 'Noble Gas',
    'lanthanide': 'Lanthanide',
    'actinide': 'Actinide',
}


class ElementButton(QtWidgets.QPushButton):
    """Custom button for periodic table elements."""
    
    def __init__(self, symbol, element_data, parent=None):
        super().__init__(parent)
        self.symbol = symbol
        self.element_data = element_data
        self.is_selected = False
        
        self.setup_button()
        
    def setup_button(self):
        """Configure button appearance."""
        self.setFixedSize(42, 48)
        self.setCheckable(True)
        
        # Set tooltip with element info
        self.setToolTip(
            f"{self.element_data['name']} ({self.symbol})\n"
            f"Atomic Number: {self.element_data['number']}\n"
            f"Atomic Mass: {self.element_data['mass']:.3f} u"
        )
        
        self.update_style()
        
    def update_style(self):
        """Update button style based on category and selection state."""
        color = CATEGORY_COLORS.get(self.element_data['category'], '#CCCCCC')
        
        if self.is_selected:
            border = "3px solid #2c3e50"
            font_weight = "bold"
        else:
            border = "1px solid #666"
            font_weight = "normal"
            
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: #2c3e50;
                border: {border};
                border-radius: 4px;
                font-size: 11px;
                font-weight: {font_weight};
                padding: 2px;
            }}
            QPushButton:hover {{
                background-color: {self._lighten_color(color)};
                border: 2px solid #2c3e50;
            }}
            QPushButton:checked {{
                border: 3px solid #e74c3c;
                background-color: {self._lighten_color(color)};
            }}
        """)
        
        # Set text with atomic number and symbol
        self.setText(f"{self.element_data['number']}\n{self.symbol}")
        
    def _lighten_color(self, hex_color):
        """Lighten a hex color by 20%."""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, int(r * 1.2))
        g = min(255, int(g * 1.2))
        b = min(255, int(b * 1.2))
        return f"#{r:02x}{g:02x}{b:02x}"


class PeriodicTable(QtWidgets.QDialog):
    """
    Modern Periodic Table Dialog with all 118 elements.
    """
    
    element_selected = QtCore.pyqtSignal(str, dict)  # Signal emitted when element is clicked
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.elements_selected = []
        self.element_buttons = {}
        
        self.setWindowTitle("Periodic Table of Elements")
        self.setMinimumSize(800, 500)
        
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the user interface."""
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QtWidgets.QLabel("Periodic Table of Elements")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; padding: 5px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter if hasattr(Qt, 'AlignmentFlag') else Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Periodic table grid
        table_widget = QtWidgets.QWidget()
        table_layout = QtWidgets.QGridLayout(table_widget)
        table_layout.setSpacing(2)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add lanthanide/actinide placeholder labels
        la_label = QtWidgets.QLabel("*")
        la_label.setStyleSheet("color: #FF9FF3; font-weight: bold; font-size: 14px;")
        la_label.setAlignment(Qt.AlignmentFlag.AlignCenter if hasattr(Qt, 'AlignmentFlag') else Qt.AlignCenter)
        table_layout.addWidget(la_label, 5, 2)
        
        ac_label = QtWidgets.QLabel("**")
        ac_label.setStyleSheet("color: #C8A2C8; font-weight: bold; font-size: 14px;")
        ac_label.setAlignment(Qt.AlignmentFlag.AlignCenter if hasattr(Qt, 'AlignmentFlag') else Qt.AlignCenter)
        table_layout.addWidget(ac_label, 6, 2)
        
        # Lanthanide label
        lan_text = QtWidgets.QLabel("* Lanthanides")
        lan_text.setStyleSheet("color: #FF9FF3; font-size: 10px;")
        table_layout.addWidget(lan_text, 8, 0, 1, 3)
        
        # Actinide label  
        act_text = QtWidgets.QLabel("** Actinides")
        act_text.setStyleSheet("color: #C8A2C8; font-size: 10px;")
        table_layout.addWidget(act_text, 9, 0, 1, 3)
        
        # Create element buttons
        for symbol, data in ELEMENTS.items():
            btn = ElementButton(symbol, data, self)
            btn.clicked.connect(lambda checked, s=symbol: self._on_element_click(s))
            self.element_buttons[symbol] = btn
            table_layout.addWidget(btn, data['row'], data['col'])
        
        main_layout.addWidget(table_widget)
        
        # Legend
        legend_widget = self._create_legend()
        main_layout.addWidget(legend_widget)
        
        # Info panel
        self.info_panel = QtWidgets.QLabel("Click an element to see details")
        self.info_panel.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 10px;
                font-size: 12px;
                color: #2c3e50;
            }
        """)
        self.info_panel.setMinimumHeight(60)
        main_layout.addWidget(self.info_panel)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        clear_btn = QtWidgets.QPushButton("Clear Selection")
        clear_btn.clicked.connect(self._clear_selection)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        button_layout.addWidget(clear_btn)
        
        button_layout.addStretch()
        
        ok_btn = QtWidgets.QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        button_layout.addWidget(cancel_btn)
        
        main_layout.addLayout(button_layout)
        
    def _create_legend(self):
        """Create the category legend."""
        legend = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(legend)
        layout.setSpacing(10)
        layout.setContentsMargins(5, 5, 5, 5)
        
        for category, color in CATEGORY_COLORS.items():
            item = QtWidgets.QWidget()
            item_layout = QtWidgets.QHBoxLayout(item)
            item_layout.setSpacing(3)
            item_layout.setContentsMargins(0, 0, 0, 0)
            
            color_box = QtWidgets.QLabel()
            color_box.setFixedSize(12, 12)
            color_box.setStyleSheet(f"background-color: {color}; border: 1px solid #666; border-radius: 2px;")
            item_layout.addWidget(color_box)
            
            label = QtWidgets.QLabel(CATEGORY_LABELS[category])
            label.setStyleSheet("font-size: 9px; color: #666;")
            item_layout.addWidget(label)
            
            layout.addWidget(item)
        
        layout.addStretch()
        return legend
        
    def _on_element_click(self, symbol):
        """Handle element button click."""
        data = ELEMENTS[symbol]
        btn = self.element_buttons[symbol]
        
        if btn.isChecked():
            if symbol not in self.elements_selected:
                self.elements_selected.append(symbol)
        else:
            if symbol in self.elements_selected:
                self.elements_selected.remove(symbol)
        
        # Update info panel
        category = CATEGORY_LABELS.get(data['category'], 'Unknown')
        self.info_panel.setText(
            f"<b>{data['name']}</b> ({symbol}) — {category}<br>"
            f"Atomic Number: {data['number']} | Atomic Mass: {data['mass']:.4f} u<br>"
            f"Selected elements: {', '.join(self.elements_selected) if self.elements_selected else 'None'}"
        )
        
        # Emit signal
        self.element_selected.emit(symbol, data)
        
    def _clear_selection(self):
        """Clear all selected elements."""
        self.elements_selected = []
        for btn in self.element_buttons.values():
            btn.setChecked(False)
        self.info_panel.setText("Selection cleared. Click an element to see details.")
        
    def update(self):
        """Update the periodic table dialog to reflect current selections."""
        for symbol, btn in self.element_buttons.items():
            btn.setChecked(symbol in self.elements_selected)
            
    def get_selected_elements(self):
        """Return list of selected element symbols."""
        return self.elements_selected.copy()
    
    def on_close(self):
        """Handle the close event for the dialog (legacy compatibility)."""
        self.accept()
