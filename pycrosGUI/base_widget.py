
"""
######## pycrosGui BaseWidget
# # part of the pycroscopy ecosystem
# #
# # by Gerd Duscher
# # Start Feb 2025
# This Base Widget is to be extended for pycroscopy GUIs
# running under python 3 using pyqt, and pyQt5 as GUI mashine
# ################################################################
"""
import os
import sys

try:
    from PyQt6 import QtCore, QtWidgets, QtGui
except ImportError:
    from PyQt5 import QtCore, QtGui, QtWidgets

import numpy as np
import pyqtgraph as pg
import sidpy

# Repository-specific imports
from .periodic_table import PeriodicTable
from .data_dialog import DataDialog

# =============================================================
#   Include pycroscopy Libraries                              #
# =============================================================
sys.path.insert(0, '../pyTEMlib/')
import pyTEMlib

class ImageView(pg.ImageView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui.roiBtn.setChecked(False)

    def roiChanged(self):
        super().roiChanged()
        for i in range(len(self.roiCurves)):
            self.roiCurves[i].setPen('black')

class MainWidget(QtWidgets.QMainWindow):
    def __init__(self, sidebar=[], filename=None):
        super().__init__()
        self.version = '2025-1-1'
        self.dataset = None
        self.datasets = {}
        self.main = ""
        self.tabCurrent = 1
        self.x = 0
        self.y = 0
        self.legend_visible = True 
        
        # Core attributes expected by the repo
        self.periodic_table = PeriodicTable(self)
        
        if filename is None:
            self.dir_name = pyTEMlib.file_tools.get_last_path()
            self.filename = ''
        else:
            self.dir_name = os.path.dirname(filename)
            self.filename = filename
        
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle(f'pycrosGUI version {self.version}qt')
        
        # MODERN STYLING: High contrast + Rounded corners + Sidebar padding
        self.setStyleSheet("""
            QMainWindow { background-color: #f0f2f5; }
            QTabWidget::pane { border: 1px solid #c9ccd1; background: #ffffff; border-radius: 8px; }
            QTabBar::tab { background: #e2e5e9; padding: 10px 20px; border: 1px solid #c9ccd1; border-top-left-radius: 8px; border-top-right-radius: 8px; margin-right: 2px; color: #333; }
            QTabBar::tab:selected { background: #ffffff; border-bottom-color: #ffffff; font-weight: bold; }
            
            QLineEdit { border: 1px solid #adb5bd; border-radius: 6px; padding: 5px; background: white; color: black; min-width: 100px; }
            QLabel { color: #212529; font-weight: bold; }
            
            /* Sidebar Styling to prevent overlap */
            QListWidget, QTreeWidget { border: 1px solid #adb5bd; border-radius: 6px; background: white; color: black; }
            QListWidget::item { padding: 12px; border-bottom: 1px solid #f0f1f2; }
            
            /* Modern Buttons */
            QPushButton { background-color: #e2e5e9; border: 1px solid #adb5bd; border-radius: 6px; padding: 6px 15px; color: #333; min-width: 90px; }
            QPushButton:hover { background-color: #d1d4d7; }
            
            QDockWidget { color: #333; font-weight: bold; }
            QDockWidget::title { background: #e2e5e9; padding: 6px; border-radius: 4px; }
        """)

        central_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout(central_widget)

        # --- Tab 1: Spectrum (Grid Layout for stability) ---
        self.plot1 = QtWidgets.QWidget()
        p1_layout = QtWidgets.QVBoxLayout(self.plot1)
        
        top_frame = QtWidgets.QFrame()
        top_frame.setStyleSheet("background-color: #f8f9fa; border-radius: 8px; border: 1px solid #dee2e6;")
        grid = QtWidgets.QGridLayout(top_frame)
        grid.setHorizontalSpacing(30)

        validfloat = QtGui.QDoubleValidator()
        self.left_cursor_label = QtWidgets.QLabel("Cursor Start")
        self.left_cursor_value = QtWidgets.QLineEdit("30.0")
        self.left_cursor_value.setValidator(validfloat)
        
        self.right_cursor_label = QtWidgets.QLabel("End")
        self.right_cursor_value = QtWidgets.QLineEdit("100.0")
        self.right_cursor_value.setValidator(validfloat)

        grid.addWidget(self.left_cursor_label, 0, 0)
        grid.addWidget(self.left_cursor_value, 0, 1)
        grid.addWidget(self.right_cursor_label, 0, 2)
        grid.addWidget(self.right_cursor_value, 0, 3)
        grid.setColumnStretch(4, 1)

        self.plot_param_window = pg.PlotWidget()
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        
        p1_layout.addWidget(top_frame)
        p1_layout.addWidget(self.plot_param_window)

        # --- Tab 2: Spectral Image ---
        self.plot2 = QtWidgets.QWidget()
        self.si_layout = QtWidgets.QGridLayout(self.plot2)
        self.si_view = pg.GraphicsView()
        self.si_img_view = pg.ViewBox()
        self.si_img_view.setAspectLocked()
        self.si_view.setCentralItem(self.si_img_view)
        self.si_plot = pg.PlotWidget()
        self.si_layout.addWidget(self.si_view, 0, 0)
        self.si_layout.addWidget(self.si_plot, 0, 1)

        # --- Tab 3: Image ---
        self.plot3 = QtWidgets.QWidget()
        p3_layout = QtWidgets.QVBoxLayout(self.plot3)
        self.title_label = QtWidgets.QLabel(" ")
        self.image_item = ImageView()
        p3_layout.addWidget(self.title_label)
        p3_layout.addWidget(self.image_item)

        self.tab = QtWidgets.QTabWidget()
        self.tab.addTab(self.plot1, 'Spectrum')
        self.tab.addTab(self.plot2, 'Spectral Image')
        self.tab.addTab(self.plot3, 'Image')
        self.tab.currentChanged.connect(self.updateTab)
        main_layout.addWidget(self.tab)
        self.setCentralWidget(central_widget)

        # Restoring compatibility for data sidebars
        self.data_dialog = DataDialog(self)
        self.data_widget = self.add_sidebar(self.data_dialog)

        self._create_menus()

    def add_sidebar(self, dialog):
        dialogWidget = QtWidgets.QDockWidget(dialog.name, self)
        dialogWidget.setFeatures(QtWidgets.QDockWidget.DockWidgetFeature.AllDockWidgetFeatures)
        dialogWidget.setWidget(dialog)
        self.addDockWidget(QtCore.Qt.DockWidgetArea.LeftDockWidgetArea, dialogWidget)
        return dialogWidget

    def _create_menus(self):
        menubar = self.menuBar()
        
        # File Menu
        self.file_menu = menubar.addMenu('&File')
        self.file_menu.addAction(QtWidgets.QAction('Open', self, shortcut='Ctrl+O', triggered=self.open_file))
        self.file_menu.addAction(QtWidgets.QAction('Save', self, shortcut='Ctrl+S', triggered=self.save_file))
        
        # RESTORED: View Menu (Required by pyTEMGui trace)
        self.view = menubar.addMenu('&View')
        
        # Window Menu
        self.window_menu = menubar.addMenu('&Windows')
        self.window_menu.addAction(QtWidgets.QAction('Restore Sidebars', self, triggered=lambda: self.data_widget.show()))

    def remove_dataset(self):
        if not self.main or self.main not in self.datasets: return
        del self.datasets[self.main]
        self.main = ""
        self.update_DataDialog()

    def open_file(self, filename=None):
        path = pyTEMlib.file_tools.get_last_path()
        if not filename:
            filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open File", path)
        if filename:
            self.main = pyTEMlib.file_tools.add_dataset_from_file(self.datasets, filename, 'Channel')
            self.update_DataDialog()

    def save_file(self, filename=None):
        if not self.datasets: return
        if not filename:
            path = pyTEMlib.file_tools.get_last_path()
            filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save File", path, "nsid Files (*.hf5)")
        if filename:
            h5_group = pyTEMlib.file_tools.save_dataset(self.datasets, filename)
            h5_group.file.close()

    def update_DataDialog(self):
        if hasattr(self.data_dialog, 'update_sidebar'):
            self.data_dialog.update_sidebar()

    def updateTab(self, num):
        self.tabCurrent = num

# Aliasing for repo compatibility
BaseWidget = MainWidget

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWidget()
    window.resize(1240, 800)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()