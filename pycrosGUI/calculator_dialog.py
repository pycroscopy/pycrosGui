"""
Advanced Scientific Calculator Dialog
Part of pycrosGUI - pycroscopy ecosystem

Features:
- Basic arithmetic operations
- Scientific functions (sin, cos, tan, log, etc.)
- Constants (pi, e, c, h, etc.)
- Expression evaluation
- History of calculations
- Unit conversions for microscopy
"""
import math
try:
    from PyQt6 import QtWidgets, QtCore, QtGui
    from PyQt6.QtCore import Qt
except ImportError:
    from PyQt5 import QtWidgets, QtCore, QtGui
    from PyQt5.QtCore import Qt


# Physical constants useful for microscopy
CONSTANTS = {
    'π': math.pi,
    'e': math.e,
    'c': 299792458,           # Speed of light (m/s)
    'h': 6.62607015e-34,      # Planck's constant (J·s)
    'ħ': 1.054571817e-34,     # Reduced Planck's constant (J·s)
    'eV': 1.602176634e-19,    # Electron volt (J)
    'me': 9.1093837015e-31,   # Electron mass (kg)
    'mp': 1.67262192369e-27,  # Proton mass (kg)
    'kB': 1.380649e-23,       # Boltzmann constant (J/K)
    'NA': 6.02214076e23,      # Avogadro's number (1/mol)
    'ε₀': 8.8541878128e-12,   # Vacuum permittivity (F/m)
    'μ₀': 1.25663706212e-6,   # Vacuum permeability (H/m)
    'a₀': 5.29177210903e-11,  # Bohr radius (m)
    'α': 7.2973525693e-3,     # Fine-structure constant
}

# Unit conversion factors
UNIT_CONVERSIONS = {
    'nm_to_A': 10,            # nanometers to angstroms
    'A_to_nm': 0.1,           # angstroms to nanometers
    'eV_to_J': 1.602176634e-19,
    'J_to_eV': 6.241509074e18,
    'nm_to_m': 1e-9,
    'm_to_nm': 1e9,
    'keV_to_eV': 1000,
    'eV_to_keV': 0.001,
    'rad_to_deg': 180 / math.pi,
    'deg_to_rad': math.pi / 180,
    'mrad_to_rad': 1e-3,
    'rad_to_mrad': 1e3,
}


class CalculatorDialog(QtWidgets.QDockWidget):
    """
    Advanced Scientific Calculator with microscopy-relevant features.
    Supports keyboard input like Desmos.
    """
    
    def __init__(self, parent=None):
        super().__init__("Scientific Calculator", parent)
        self.parent = parent
        self.history = []
        self.memory = 0
        self.current_expression = ""
        self.last_result = 0
        
        self.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
                             if hasattr(Qt, 'DockWidgetArea') else Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the calculator interface."""
        main_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(main_widget)
        layout.setSpacing(5)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Display - now editable for keyboard input like Desmos
        display_layout = QtWidgets.QVBoxLayout()
        
        # Expression input (editable - users can type here)
        self.expression_input = QtWidgets.QLineEdit()
        self.expression_input.setPlaceholderText("Type expression here (e.g., 2+3*sin(pi/4))...")
        self.expression_input.setAlignment(Qt.AlignmentFlag.AlignLeft if hasattr(Qt, 'AlignmentFlag') else Qt.AlignLeft)
        self.expression_input.setStyleSheet("""
            QLineEdit {
                background-color: #ffffff;
                color: #2c3e50;
                border: 2px solid #3498db;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
                font-family: monospace;
            }
            QLineEdit:focus {
                border: 2px solid #2980b9;
                background-color: #f8f9fa;
            }
        """)
        self.expression_input.textChanged.connect(self._on_text_changed)
        self.expression_input.returnPressed.connect(self._evaluate)
        display_layout.addWidget(self.expression_input)
        
        # Result display (read-only, shows live result)
        self.result_display = QtWidgets.QLineEdit("0")
        self.result_display.setReadOnly(True)
        self.result_display.setAlignment(Qt.AlignmentFlag.AlignRight if hasattr(Qt, 'AlignmentFlag') else Qt.AlignRight)
        self.result_display.setStyleSheet("""
            QLineEdit {
                background-color: #2c3e50;
                color: #2ecc71;
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-size: 22px;
                font-weight: bold;
                font-family: monospace;
            }
        """)
        display_layout.addWidget(self.result_display)
        
        layout.addLayout(display_layout)
        
        # Create tabs for different button groups - FIXED STYLING
        tab_widget = QtWidgets.QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: #f8f9fa;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                color: #2c3e50;
                padding: 8px 14px;
                margin-right: 2px;
                border-radius: 4px 4px 0 0;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background-color: #d5dbdb;
            }
        """)
        
        # Basic tab
        basic_tab = self._create_basic_buttons()
        tab_widget.addTab(basic_tab, "Basic")
        
        # Scientific tab
        scientific_tab = self._create_scientific_buttons()
        tab_widget.addTab(scientific_tab, "Scientific")
        
        # Constants tab
        constants_tab = self._create_constants_buttons()
        tab_widget.addTab(constants_tab, "Constants")
        
        # Conversions tab
        conversions_tab = self._create_conversion_panel()
        tab_widget.addTab(conversions_tab, "Convert")
        
        layout.addWidget(tab_widget)
        
        # History section
        history_group = QtWidgets.QGroupBox("History")
        history_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
            }
        """)
        history_layout = QtWidgets.QVBoxLayout(history_group)
        
        self.history_list = QtWidgets.QListWidget()
        self.history_list.setMaximumHeight(80)
        self.history_list.setStyleSheet("""
            QListWidget {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                font-family: monospace;
                font-size: 10px;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        self.history_list.itemDoubleClicked.connect(self._use_history_item)
        history_layout.addWidget(self.history_list)
        
        clear_history_btn = QtWidgets.QPushButton("Clear History")
        clear_history_btn.clicked.connect(self._clear_history)
        clear_history_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        history_layout.addWidget(clear_history_btn)
        
        layout.addWidget(history_group)
        
        self.setWidget(main_widget)
        
    def _create_button(self, text, callback, style="default"):
        """Create a styled calculator button."""
        btn = QtWidgets.QPushButton(text)
        btn.setMinimumSize(40, 35)
        # Connect with a wrapper that ignores the 'checked' argument from clicked signal
        btn.clicked.connect(lambda checked, cb=callback: cb())
        
        styles = {
            "default": """
                QPushButton {
                    background-color: #ecf0f1;
                    color: #2c3e50;
                    border: 1px solid #bdc3c7;
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #d5dbdb;
                }
                QPushButton:pressed {
                    background-color: #bdc3c7;
                }
            """,
            "number": """
                QPushButton {
                    background-color: #ffffff;
                    color: #2c3e50;
                    border: 1px solid #bdc3c7;
                    border-radius: 4px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #f5f5f5;
                }
                QPushButton:pressed {
                    background-color: #e0e0e0;
                }
            """,
            "operator": """
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QPushButton:pressed {
                    background-color: #1f6aa5;
                }
            """,
            "equals": """
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #219a52;
                }
                QPushButton:pressed {
                    background-color: #1e8449;
                }
            """,
            "clear": """
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """,
            "function": """
                QPushButton {
                    background-color: #9b59b6;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #8e44ad;
                }
            """,
            "constant": """
                QPushButton {
                    background-color: #1abc9c;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #16a085;
                }
            """,
        }
        
        btn.setStyleSheet(styles.get(style, styles["default"]))
        return btn
        
    def _create_basic_buttons(self):
        """Create basic calculator buttons."""
        widget = QtWidgets.QWidget()
        grid = QtWidgets.QGridLayout(widget)
        grid.setSpacing(3)
        
        # Clear buttons row
        grid.addWidget(self._create_button("C", self._clear, "clear"), 0, 0)
        grid.addWidget(self._create_button("CE", self._clear_entry, "clear"), 0, 1)
        grid.addWidget(self._create_button("⌫", self._backspace, "default"), 0, 2)
        grid.addWidget(self._create_button("÷", lambda: self._add_operator("/"), "operator"), 0, 3)
        
        # Number rows - each button with explicit operator mapping
        numbers = [
            [('7', '7'), ('8', '8'), ('9', '9'), ('×', '*')],
            [('4', '4'), ('5', '5'), ('6', '6'), ('-', '-')],
            [('1', '1'), ('2', '2'), ('3', '3'), ('+', '+')],
            [('±', '±'), ('0', '0'), ('.', '.'), ('=', '=')],
        ]
        
        for row, items in enumerate(numbers, 1):
            for col, (label, value) in enumerate(items):
                if value.isdigit() or value == '.':
                    btn = self._create_button(label, lambda v=value: self._add_digit(v), "number")
                elif value == '=':
                    btn = self._create_button(label, self._evaluate, "equals")
                elif value == '±':
                    btn = self._create_button(label, self._toggle_sign, "default")
                else:
                    # Operators: *, -, +
                    btn = self._create_button(label, lambda op=value: self._add_operator(op), "operator")
                grid.addWidget(btn, row, col)
        
        # Memory buttons
        memory_layout = QtWidgets.QHBoxLayout()
        memory_layout.addWidget(self._create_button("MC", self._memory_clear, "default"))
        memory_layout.addWidget(self._create_button("MR", self._memory_recall, "default"))
        memory_layout.addWidget(self._create_button("M+", self._memory_add, "default"))
        memory_layout.addWidget(self._create_button("M-", self._memory_subtract, "default"))
        
        grid.addLayout(memory_layout, 5, 0, 1, 4)
        
        return widget
        
    def _create_scientific_buttons(self):
        """Create scientific function buttons."""
        widget = QtWidgets.QWidget()
        grid = QtWidgets.QGridLayout(widget)
        grid.setSpacing(3)
        
        # Scientific functions
        functions = [
            [('sin', 'sin'), ('cos', 'cos'), ('tan', 'tan'), ('π', 'pi')],
            [('sin⁻¹', 'asin'), ('cos⁻¹', 'acos'), ('tan⁻¹', 'atan'), ('e', 'e')],
            [('ln', 'log'), ('log₁₀', 'log10'), ('log₂', 'log2'), ('eˣ', 'exp')],
            [('x²', 'square'), ('x³', 'cube'), ('√', 'sqrt'), ('∛', 'cbrt')],
            [('xʸ', 'pow'), ('10ˣ', 'pow10'), ('|x|', 'abs'), ('1/x', 'inv')],
            [('n!', 'fact'), ('(', 'lparen'), (')', 'rparen'), ('mod', 'mod')],
        ]
        
        for row, items in enumerate(functions):
            for col, (label, func) in enumerate(items):
                btn = self._create_button(label, lambda f=func: self._add_function(f), "function")
                grid.addWidget(btn, row, col)
        
        return widget
        
    def _create_constants_buttons(self):
        """Create physical constants buttons."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        
        # Description label
        desc = QtWidgets.QLabel("Physical constants for microscopy calculations:")
        desc.setStyleSheet("color: #666; font-size: 10px; padding: 5px;")
        layout.addWidget(desc)
        
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QtWidgets.QWidget()
        grid = QtWidgets.QGridLayout(scroll_widget)
        grid.setSpacing(3)
        
        constant_info = {
            'π': ('π', 'Pi (3.14159...)'),
            'e': ('e', 'Euler number (2.71828...)'),
            'c': ('c', 'Speed of light (m/s)'),
            'h': ('h', "Planck's constant (J·s)"),
            'ħ': ('ħ', "Reduced Planck's constant"),
            'eV': ('eV', 'Electron volt (J)'),
            'me': ('mₑ', 'Electron mass (kg)'),
            'mp': ('mₚ', 'Proton mass (kg)'),
            'kB': ('kB', 'Boltzmann constant (J/K)'),
            'NA': ('Nₐ', "Avogadro's number"),
            'ε₀': ('ε₀', 'Vacuum permittivity (F/m)'),
            'μ₀': ('μ₀', 'Vacuum permeability (H/m)'),
            'a₀': ('a₀', 'Bohr radius (m)'),
            'α': ('α', 'Fine-structure constant'),
        }
        
        for i, (key, (label, tooltip)) in enumerate(constant_info.items()):
            btn = self._create_button(label, lambda k=key: self._insert_constant(k), "constant")
            btn.setToolTip(f"{tooltip}\n= {CONSTANTS[key]:.6e}")
            grid.addWidget(btn, i // 4, i % 4)
        
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        return widget
        
    def _create_conversion_panel(self):
        """Create unit conversion panel."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setSpacing(10)
        
        # Conversion type selector
        self.conversion_combo = QtWidgets.QComboBox()
        self.conversion_combo.addItems([
            "nm ↔ Å (Length)",
            "eV ↔ J (Energy)",
            "keV ↔ eV (Energy)",
            "° ↔ rad (Angle)",
            "mrad ↔ rad (Angle)",
            "nm ↔ m (Length)",
        ])
        self.conversion_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                color: #2c3e50;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #2c3e50;
                selection-background-color: #3498db;
                selection-color: white;
            }
        """)
        layout.addWidget(self.conversion_combo)
        
        # Input/Output
        io_layout = QtWidgets.QGridLayout()
        
        input_label = QtWidgets.QLabel("Input:")
        input_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
        io_layout.addWidget(input_label, 0, 0)
        self.conv_input = QtWidgets.QLineEdit()
        self.conv_input.setPlaceholderText("Enter value...")
        self.conv_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                color: #2c3e50;
            }
        """)
        io_layout.addWidget(self.conv_input, 0, 1)
        
        result_label = QtWidgets.QLabel("Result:")
        result_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
        io_layout.addWidget(result_label, 1, 0)
        self.conv_output = QtWidgets.QLineEdit()
        self.conv_output.setReadOnly(True)
        self.conv_output.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: #f8f9fa;
                color: #2c3e50;
            }
        """)
        io_layout.addWidget(self.conv_output, 1, 1)
        
        layout.addLayout(io_layout)
        
        # Convert buttons
        btn_layout = QtWidgets.QHBoxLayout()
        
        convert_btn = QtWidgets.QPushButton("Convert →")
        convert_btn.clicked.connect(lambda: self._do_conversion(forward=True))
        convert_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        btn_layout.addWidget(convert_btn)
        
        convert_rev_btn = QtWidgets.QPushButton("← Convert")
        convert_rev_btn.clicked.connect(lambda: self._do_conversion(forward=False))
        convert_rev_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        btn_layout.addWidget(convert_rev_btn)
        
        layout.addLayout(btn_layout)
        
        # Wavelength-energy converter (useful for microscopy)
        layout.addWidget(QtWidgets.QLabel(""))  # Spacer
        
        energy_group = QtWidgets.QGroupBox("Wavelength ↔ Energy")
        energy_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #2c3e50;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        energy_layout = QtWidgets.QVBoxLayout(energy_group)
        
        wl_layout = QtWidgets.QHBoxLayout()
        wl_label = QtWidgets.QLabel("λ (nm):")
        wl_label.setStyleSheet("color: #2c3e50;")
        wl_layout.addWidget(wl_label)
        self.wavelength_input = QtWidgets.QLineEdit()
        self.wavelength_input.setPlaceholderText("wavelength")
        self.wavelength_input.setStyleSheet("""
            QLineEdit {
                padding: 6px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                color: #2c3e50;
            }
        """)
        wl_layout.addWidget(self.wavelength_input)
        energy_layout.addLayout(wl_layout)
        
        ev_layout = QtWidgets.QHBoxLayout()
        ev_label = QtWidgets.QLabel("E (eV):")
        ev_label.setStyleSheet("color: #2c3e50;")
        ev_layout.addWidget(ev_label)
        self.energy_output = QtWidgets.QLineEdit()
        self.energy_output.setReadOnly(True)
        self.energy_output.setStyleSheet("""
            QLineEdit {
                padding: 6px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: #f8f9fa;
                color: #2c3e50;
            }
        """)
        ev_layout.addWidget(self.energy_output)
        energy_layout.addLayout(ev_layout)
        
        calc_energy_btn = QtWidgets.QPushButton("λ → E")
        calc_energy_btn.clicked.connect(self._wavelength_to_energy)
        calc_energy_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        energy_layout.addWidget(calc_energy_btn)
        
        layout.addWidget(energy_group)
        layout.addStretch()
        
        return widget
        
    # Calculator operations
    def _on_text_changed(self, text):
        """Handle text changes - live evaluation like Desmos."""
        self.current_expression = text
        if text:
            try:
                result = self._safe_eval(text)
                if isinstance(result, float):
                    if abs(result) > 1e10 or (abs(result) < 1e-6 and result != 0):
                        self.result_display.setText(f"{result:.6e}")
                    else:
                        self.result_display.setText(f"{result:.10g}")
                else:
                    self.result_display.setText(str(result))
                self.result_display.setStyleSheet("""
                    QLineEdit {
                        background-color: #2c3e50;
                        color: #2ecc71;
                        border: none;
                        border-radius: 6px;
                        padding: 12px;
                        font-size: 22px;
                        font-weight: bold;
                        font-family: monospace;
                    }
                """)
            except:
                self.result_display.setText("...")
                self.result_display.setStyleSheet("""
                    QLineEdit {
                        background-color: #2c3e50;
                        color: #95a5a6;
                        border: none;
                        border-radius: 6px;
                        padding: 12px;
                        font-size: 22px;
                        font-weight: bold;
                        font-family: monospace;
                    }
                """)
        else:
            self.result_display.setText("0")
            
    def _add_digit(self, digit):
        """Add a digit to the current expression."""
        cursor_pos = self.expression_input.cursorPosition()
        text = self.expression_input.text()
        new_text = text[:cursor_pos] + digit + text[cursor_pos:]
        self.expression_input.setText(new_text)
        self.expression_input.setCursorPosition(cursor_pos + len(digit))
        self.expression_input.setFocus()
        
    def _add_operator(self, op):
        """Add an operator to the expression."""
        cursor_pos = self.expression_input.cursorPosition()
        text = self.expression_input.text()
        new_text = text[:cursor_pos] + op + text[cursor_pos:]
        self.expression_input.setText(new_text)
        self.expression_input.setCursorPosition(cursor_pos + len(op))
        self.expression_input.setFocus()
        
    def _add_function(self, func):
        """Add a function to the expression."""
        insert_text = ""
        if func == 'pi':
            insert_text = 'pi'
        elif func == 'e':
            insert_text = 'e'
        elif func == 'lparen':
            insert_text = '('
        elif func == 'rparen':
            insert_text = ')'
        elif func == 'mod':
            insert_text = '%'
        elif func == 'square':
            insert_text = '^2'
        elif func == 'cube':
            insert_text = '^3'
        elif func == 'pow':
            insert_text = '^'
        elif func == 'pow10':
            insert_text = '10^'
        elif func == 'inv':
            insert_text = '1/'
        elif func == 'fact':
            insert_text = 'factorial('
        elif func == 'cbrt':
            insert_text = 'cbrt('
        elif func in ['sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'log', 'log10', 'log2', 'exp', 'sqrt', 'abs']:
            insert_text = f'{func}('
        
        if insert_text:
            cursor_pos = self.expression_input.cursorPosition()
            text = self.expression_input.text()
            new_text = text[:cursor_pos] + insert_text + text[cursor_pos:]
            self.expression_input.setText(new_text)
            self.expression_input.setCursorPosition(cursor_pos + len(insert_text))
            self.expression_input.setFocus()
        
    def _insert_constant(self, key):
        """Insert a physical constant value."""
        cursor_pos = self.expression_input.cursorPosition()
        text = self.expression_input.text()
        value_str = str(CONSTANTS[key])
        new_text = text[:cursor_pos] + value_str + text[cursor_pos:]
        self.expression_input.setText(new_text)
        self.expression_input.setCursorPosition(cursor_pos + len(value_str))
        self.expression_input.setFocus()
        
    def _toggle_sign(self):
        """Toggle the sign of the expression."""
        text = self.expression_input.text()
        if text:
            if text.startswith('-'):
                self.expression_input.setText(text[1:])
            else:
                self.expression_input.setText('-' + text)
        self.expression_input.setFocus()
            
    def _clear(self):
        """Clear all."""
        self.expression_input.clear()
        self.result_display.setText("0")
        self.current_expression = ""
        self.expression_input.setFocus()
        
    def _clear_entry(self):
        """Clear current entry."""
        self.expression_input.clear()
        self.current_expression = ""
        self.expression_input.setFocus()
        
    def _backspace(self):
        """Remove last character."""
        self.expression_input.backspace()
        self.expression_input.setFocus()
        
    def _memory_clear(self):
        """Clear memory."""
        self.memory = 0
        
    def _memory_recall(self):
        """Recall memory value."""
        self.current_expression += str(self.memory)
        self._update_display()
        
    def _memory_add(self):
        """Add current result to memory."""
        try:
            self.memory += float(self.result_display.text())
        except:
            pass
            
    def _memory_subtract(self):
        """Subtract current result from memory."""
        try:
            self.memory -= float(self.result_display.text())
        except:
            pass
            
    def _safe_eval(self, expr):
        """Safely evaluate a mathematical expression with natural syntax like Desmos."""
        import re
        
        # Normalize the expression
        expr = expr.strip()
        if not expr:
            raise ValueError("Empty expression")
        
        # Replace display operators with Python operators
        expr = expr.replace('×', '*').replace('÷', '/').replace('−', '-')
        
        # Replace ^ with ** for exponentiation
        expr = expr.replace('^', '**')
        
        # List of function names to protect from implicit multiplication
        func_names = ['sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'sinh', 'cosh', 'tanh',
                      'log', 'log10', 'log2', 'exp', 'sqrt', 'cbrt', 'abs', 'floor', 'ceil',
                      'round', 'factorial', 'ln']
        
        # Replace common function names (case insensitive)
        # ln -> log (natural log)
        expr = re.sub(r'\bln\b', 'log', expr, flags=re.IGNORECASE)
        
        # Add implicit multiplication: 2pi -> 2*pi, 3(4) -> 3*(4), (2)(3) -> (2)*(3)
        # But NOT after function names like sin, cos, etc.
        
        # First, temporarily replace function names with placeholders
        placeholders = {}
        for i, func in enumerate(func_names):
            placeholder = f"__FUNC{i}__"
            placeholders[placeholder] = func
            expr = re.sub(rf'\b{func}\b', placeholder, expr, flags=re.IGNORECASE)
        
        # Number followed by letter (but not already a placeholder) or opening paren
        expr = re.sub(r'(\d)([a-zA-Z(])', r'\1*\2', expr)
        # Closing paren followed by opening paren or letter or number
        expr = re.sub(r'(\))([a-zA-Z0-9(])', r'\1*\2', expr)
        
        # Restore function names
        for placeholder, func in placeholders.items():
            # Remove any * that got inserted between function and its opening paren
            expr = expr.replace(f"{placeholder}*(", f"{func}(")
            expr = expr.replace(placeholder, func)
        
        # Define cube root function
        def cbrt(x):
            if x >= 0:
                return x ** (1/3)
            else:
                return -((-x) ** (1/3))
        
        # Only allow safe operations
        allowed_names = {
            'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
            'asin': math.asin, 'acos': math.acos, 'atan': math.atan,
            'sinh': math.sinh, 'cosh': math.cosh, 'tanh': math.tanh,
            'log': math.log, 'log10': math.log10, 'log2': math.log2,
            'exp': math.exp, 'sqrt': math.sqrt, 'cbrt': cbrt,
            'abs': abs, 'floor': math.floor, 'ceil': math.ceil,
            'round': round,
            'pi': math.pi, 'e': math.e,
            'pow': pow, 'factorial': math.factorial,
        }
        
        try:
            result = eval(expr, {"__builtins__": {}}, allowed_names)
            return result
        except Exception as e:
            raise ValueError(str(e))
            
    def _evaluate(self):
        """Evaluate the current expression and add to history."""
        expr = self.expression_input.text().strip()
        if not expr:
            return
            
        try:
            result = self._safe_eval(expr)
            
            # Format result
            if isinstance(result, float):
                if abs(result) > 1e10 or (abs(result) < 1e-6 and result != 0):
                    result_str = f"{result:.6e}"
                else:
                    result_str = f"{result:.10g}"
            else:
                result_str = str(result)
            
            # Add to history
            history_entry = f"{expr} = {result_str}"
            self.history.append(history_entry)
            self.history_list.addItem(history_entry)
            self.history_list.scrollToBottom()
            
            self.last_result = result
            self.result_display.setText(result_str)
            
            # Set the result as the new expression for continued calculation
            self.expression_input.setText(result_str)
            self.expression_input.selectAll()
            
        except Exception as e:
            self.result_display.setText("Error")
            self.result_display.setStyleSheet("""
                QLineEdit {
                    background-color: #2c3e50;
                    color: #e74c3c;
                    border: none;
                    border-radius: 6px;
                    padding: 12px;
                    font-size: 22px;
                    font-weight: bold;
                    font-family: monospace;
                }
            """)
            
    def _use_history_item(self, item):
        """Use a history item - set expression to the equation."""
        text = item.text()
        if '=' in text:
            # Get the expression part (before the =)
            expr = text.split('=')[0].strip()
            self.expression_input.setText(expr)
            self.expression_input.setFocus()
            
    def _clear_history(self):
        """Clear calculation history."""
        self.history = []
        self.history_list.clear()
        
    def _do_conversion(self, forward=True):
        """Perform unit conversion."""
        try:
            value = float(self.conv_input.text())
            conv_type = self.conversion_combo.currentIndex()
            
            conversions = [
                ('nm_to_A', 'A_to_nm'),
                ('eV_to_J', 'J_to_eV'),
                ('keV_to_eV', 'eV_to_keV'),
                ('deg_to_rad', 'rad_to_deg'),
                ('mrad_to_rad', 'rad_to_mrad'),
                ('nm_to_m', 'm_to_nm'),
            ]
            
            if forward:
                factor = UNIT_CONVERSIONS[conversions[conv_type][0]]
            else:
                factor = UNIT_CONVERSIONS[conversions[conv_type][1]]
            
            result = value * factor
            
            if abs(result) > 1e6 or (abs(result) < 1e-3 and result != 0):
                self.conv_output.setText(f"{result:.6e}")
            else:
                self.conv_output.setText(f"{result:.6g}")
                
        except ValueError:
            self.conv_output.setText("Invalid input")
            
    def _wavelength_to_energy(self):
        """Convert wavelength to energy."""
        try:
            wavelength_nm = float(self.wavelength_input.text())
            wavelength_m = wavelength_nm * 1e-9
            
            # E = hc/λ
            energy_j = CONSTANTS['h'] * CONSTANTS['c'] / wavelength_m
            energy_ev = energy_j / CONSTANTS['eV']
            
            self.energy_output.setText(f"{energy_ev:.4f}")
        except ValueError:
            self.energy_output.setText("Invalid input")
            
    def get_sidebar(self):
        """Return the calculator widget for sidebar integration."""
        return self.widget()


# For standalone testing
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    calc = CalculatorDialog()
    calc.show()
    sys.exit(app.exec() if hasattr(app, 'exec') else app.exec_())
