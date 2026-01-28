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
        
        # Display
        display_layout = QtWidgets.QVBoxLayout()
        
        # Expression display (smaller, shows the expression)
        self.expression_display = QtWidgets.QLineEdit()
        self.expression_display.setReadOnly(True)
        self.expression_display.setAlignment(Qt.AlignmentFlag.AlignRight if hasattr(Qt, 'AlignmentFlag') else Qt.AlignRight)
        self.expression_display.setStyleSheet("""
            QLineEdit {
                background-color: #2c3e50;
                color: #95a5a6;
                border: none;
                border-radius: 4px;
                padding: 5px;
                font-size: 11px;
                font-family: monospace;
            }
        """)
        display_layout.addWidget(self.expression_display)
        
        # Result display (larger)
        self.result_display = QtWidgets.QLineEdit("0")
        self.result_display.setReadOnly(True)
        self.result_display.setAlignment(Qt.AlignmentFlag.AlignRight if hasattr(Qt, 'AlignmentFlag') else Qt.AlignRight)
        self.result_display.setStyleSheet("""
            QLineEdit {
                background-color: #34495e;
                color: #ecf0f1;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-size: 20px;
                font-weight: bold;
                font-family: monospace;
            }
        """)
        display_layout.addWidget(self.result_display)
        
        layout.addLayout(display_layout)
        
        # Create tabs for different button groups
        tab_widget = QtWidgets.QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                padding: 6px 12px;
                margin-right: 2px;
                border-radius: 4px 4px 0 0;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
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
        btn.clicked.connect(callback)
        
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
        
        # Number rows
        numbers = [
            ['7', '8', '9', '×'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+'],
            ['±', '0', '.', '='],
        ]
        
        for row, items in enumerate(numbers, 1):
            for col, item in enumerate(items):
                if item.isdigit() or item == '.':
                    btn = self._create_button(item, lambda x=item: self._add_digit(x), "number")
                elif item == '=':
                    btn = self._create_button(item, self._evaluate, "equals")
                elif item == '±':
                    btn = self._create_button(item, self._toggle_sign, "default")
                elif item == '×':
                    btn = self._create_button(item, lambda: self._add_operator("*"), "operator")
                else:
                    btn = self._create_button(item, lambda op=item: self._add_operator(op), "operator")
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
            }
        """)
        layout.addWidget(self.conversion_combo)
        
        # Input/Output
        io_layout = QtWidgets.QGridLayout()
        
        io_layout.addWidget(QtWidgets.QLabel("Input:"), 0, 0)
        self.conv_input = QtWidgets.QLineEdit()
        self.conv_input.setPlaceholderText("Enter value...")
        self.conv_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
        """)
        io_layout.addWidget(self.conv_input, 0, 1)
        
        io_layout.addWidget(QtWidgets.QLabel("Result:"), 1, 0)
        self.conv_output = QtWidgets.QLineEdit()
        self.conv_output.setReadOnly(True)
        self.conv_output.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: #f8f9fa;
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
        energy_layout = QtWidgets.QVBoxLayout(energy_group)
        
        wl_layout = QtWidgets.QHBoxLayout()
        wl_layout.addWidget(QtWidgets.QLabel("λ (nm):"))
        self.wavelength_input = QtWidgets.QLineEdit()
        self.wavelength_input.setPlaceholderText("wavelength")
        wl_layout.addWidget(self.wavelength_input)
        energy_layout.addLayout(wl_layout)
        
        ev_layout = QtWidgets.QHBoxLayout()
        ev_layout.addWidget(QtWidgets.QLabel("E (eV):"))
        self.energy_output = QtWidgets.QLineEdit()
        self.energy_output.setReadOnly(True)
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
    def _add_digit(self, digit):
        """Add a digit to the current expression."""
        self.current_expression += digit
        self._update_display()
        
    def _add_operator(self, op):
        """Add an operator to the expression."""
        self.current_expression += f" {op} "
        self._update_display()
        
    def _add_function(self, func):
        """Add a function to the expression."""
        if func == 'pi':
            self.current_expression += str(math.pi)
        elif func == 'e':
            self.current_expression += str(math.e)
        elif func == 'lparen':
            self.current_expression += '('
        elif func == 'rparen':
            self.current_expression += ')'
        elif func == 'mod':
            self.current_expression += ' % '
        elif func == 'square':
            self.current_expression += '**2'
        elif func == 'cube':
            self.current_expression += '**3'
        elif func == 'pow':
            self.current_expression += '**'
        elif func == 'pow10':
            self.current_expression = f'10**({self.current_expression})'
        elif func == 'inv':
            self.current_expression = f'1/({self.current_expression})'
        elif func == 'fact':
            try:
                n = int(float(self._safe_eval(self.current_expression)))
                self.current_expression = str(math.factorial(n))
            except:
                self.current_expression = "Error"
        elif func == 'cbrt':
            self.current_expression = f'({self.current_expression})**(1/3)'
        elif func in ['sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'log', 'log10', 'log2', 'exp', 'sqrt', 'abs']:
            self.current_expression = f'math.{func}({self.current_expression})'
        
        self._update_display()
        
    def _insert_constant(self, key):
        """Insert a physical constant value."""
        self.current_expression += str(CONSTANTS[key])
        self._update_display()
        
    def _toggle_sign(self):
        """Toggle the sign of the current number."""
        if self.current_expression:
            if self.current_expression.startswith('-'):
                self.current_expression = self.current_expression[1:]
            else:
                self.current_expression = '-' + self.current_expression
            self._update_display()
            
    def _clear(self):
        """Clear all."""
        self.current_expression = ""
        self.result_display.setText("0")
        self.expression_display.setText("")
        
    def _clear_entry(self):
        """Clear current entry."""
        self.current_expression = ""
        self._update_display()
        
    def _backspace(self):
        """Remove last character."""
        self.current_expression = self.current_expression.rstrip()
        if self.current_expression:
            self.current_expression = self.current_expression[:-1]
        self._update_display()
        
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
        """Safely evaluate a mathematical expression."""
        # Replace display operators with Python operators
        expr = expr.replace('×', '*').replace('÷', '/')
        
        # Only allow safe operations
        allowed_names = {
            'math': math,
            'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
            'asin': math.asin, 'acos': math.acos, 'atan': math.atan,
            'log': math.log, 'log10': math.log10, 'log2': math.log2,
            'exp': math.exp, 'sqrt': math.sqrt, 'abs': abs,
            'pi': math.pi, 'e': math.e,
            'pow': pow, 'factorial': math.factorial,
        }
        
        try:
            return eval(expr, {"__builtins__": {}}, allowed_names)
        except Exception as e:
            raise ValueError(str(e))
            
    def _evaluate(self):
        """Evaluate the current expression."""
        if not self.current_expression:
            return
            
        try:
            result = self._safe_eval(self.current_expression)
            
            # Format result
            if isinstance(result, float):
                if abs(result) > 1e10 or (abs(result) < 1e-6 and result != 0):
                    result_str = f"{result:.6e}"
                else:
                    result_str = f"{result:.10g}"
            else:
                result_str = str(result)
            
            # Add to history
            history_entry = f"{self.current_expression} = {result_str}"
            self.history.append(history_entry)
            self.history_list.addItem(history_entry)
            self.history_list.scrollToBottom()
            
            self.last_result = result
            self.result_display.setText(result_str)
            self.expression_display.setText(self.current_expression)
            self.current_expression = result_str
            
        except Exception as e:
            self.result_display.setText("Error")
            self.expression_display.setText(str(e))
            
    def _update_display(self):
        """Update the expression display."""
        self.expression_display.setText(self.current_expression if self.current_expression else "")
        if self.current_expression:
            # Try to show live evaluation
            try:
                result = self._safe_eval(self.current_expression)
                if isinstance(result, float):
                    self.result_display.setText(f"{result:.10g}")
                else:
                    self.result_display.setText(str(result))
            except:
                pass
                
    def _use_history_item(self, item):
        """Use a history item's result."""
        text = item.text()
        if '=' in text:
            result = text.split('=')[-1].strip()
            self.current_expression = result
            self._update_display()
            
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
