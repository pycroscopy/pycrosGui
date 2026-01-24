
"""
######## pycrosGui BaseWidget
# # part of the pycroscopy ecosystem
# #
# # by Gerd Duscher and Levi Dunn
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

class BaseWidget(QtWidgets.QMainWindow):
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
        
        if filename is None:
            self.dir_name = pyTEMlib.file_tools.get_last_path()
            self.filename = ''
        else:
            self.dir_name = os.path.dirname(filename)
            self.filename = filename
        
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle(f'pycrosGUI version {self.version}qt')
        
        # MODERN STYLING: Fixes overlap, white-on-white, and adds rounded corners
        self.setStyleSheet("""
            QMainWindow { background-color: #f0f2f5; }
            QTabWidget::pane { border: 1px solid #c9ccd1; background: #ffffff; border-radius: 8px; }
            QTabBar::tab { background: #e2e5e9; padding: 10px 20px; border: 1px solid #c9ccd1; border-top-left-radius: 8px; border-top-right-radius: 8px; margin-right: 2px; color: #333; }
            QTabBar::tab:selected { background: #ffffff; border-bottom-color: #ffffff; font-weight: bold; }
            
            QLineEdit { border: 1px solid #adb5bd; border-radius: 6px; padding: 5px; background: white; color: black; min-width: 100px; }
            QLabel { color: #212529; font-weight: bold; }
            
            /* Sidebar Styling */
            QListWidget, QTreeWidget { border: 1px solid #adb5bd; border-radius: 6px; background: white; color: black; margin-bottom: 5px; }
            QListWidget::item { padding: 8px; border-bottom: 1px solid #eee; }
            
            QPushButton { background-color: #e2e5e9; border: 1px solid #adb5bd; border-radius: 4px; padding: 5px 15px; color: #333; min-width: 80px; }
            QPushButton:hover { background-color: #d1d4d7; }
            
            QDockWidget { color: #333; font-weight: bold; }
            QDockWidget::title { background: #e2e5e9; padding: 6px; border-radius: 4px; }
        """)

        central_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout(central_widget)

        # --- Tab 1: Spectrum ---
        self.plot1 = QtWidgets.QWidget()
        p1_layout = QtWidgets.QVBoxLayout(self.plot1)
        
        top_frame = QtWidgets.QFrame()
        top_frame.setStyleSheet("background-color: #f8f9fa; border-radius: 8px; border: 1px solid #dee2e6;")
        grid = QtWidgets.QGridLayout(top_frame)
        grid.setHorizontalSpacing(25)

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

        # --- Sidebars ---
        self.data_widget = QtWidgets.QDockWidget("Datasets", self)
        self.data_dialog = DataDialog(self) 
        self.data_widget.setWidget(self.data_dialog)
        self.addDockWidget(QtCore.Qt.DockWidgetArea.LeftDockWidgetArea, self.data_widget)

        self.select_widget = QtWidgets.QDockWidget("Select", self)
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self.select_widget)

        self._create_menus()

    def _create_menus(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(QtWidgets.QAction('Open', self, shortcut='Ctrl+O', triggered=self.open_file))
        file_menu.addAction(QtWidgets.QAction('Save', self, shortcut='Ctrl+S', triggered=self.save_file))
        
        window_menu = menubar.addMenu('&Windows')
        window_menu.addAction(QtWidgets.QAction('Restore Sidebars', self, triggered=self.restore_sidebars))

    def restore_sidebars(self):
        self.data_widget.show()
        self.select_widget.show()

    def remove_dataset(self):
        """Action for the 'Remove' button in the sidebar."""
        if self.main in self.datasets:
            del self.datasets[self.main]
            self.main = ""
            self.update_DataDialog()
            self.status_msg("Dataset Removed")

    def open_file(self, filename=None):
        path = pyTEMlib.file_tools.get_last_path()
        if not filename:
            filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open File", path)
        if filename:
            self.main = pyTEMlib.file_tools.add_dataset_from_file(self.datasets, filename, 'Channel')
            self.update_DataDialog()

    def save_file(self, filename=None):
        if not self.main: return
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save File", filter="nsid Files (*.hf5)")
        if file_name:
            h5 = pyTEMlib.file_tools.save_dataset(self.datasets, file_name)
            h5.file.close()
            self.status_msg("File Saved")

    def status_msg(self, text):
        self.statusBar().showMessage(text)

    def updateTab(self, num):
        self.tabCurrent = num

    def update_DataDialog(self):
        if hasattr(self.data_dialog, 'update_sidebar'):
            self.data_dialog.update_sidebar()

    def imageHoverEvent(self, event):
        pass

    def mouse_clicked_image(self, event):
        pass

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = BaseWidget()
    window.resize(1240, 800)
    window.show()
    sys.exit(app.exec())