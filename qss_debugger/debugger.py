# Copyright 2018 Ruben Henares
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# *********************************************************************
# +++ IMPORTS
# *********************************************************************
import os

from Qt import QtGui, QtCore, QtWidgets

from qss_debugger.explorer import VisualTreeExplorer
from qss_debugger.painter import VisualTreePainter
from qss_debugger.compiler import VisualCompilerDefault


# *********************************************************************
# +++ CLASSES
# *********************************************************************
class VisualTreeEventFilter(QtCore.QObject):
    # =====================================================================
    # +++ SIGNALS
    # =====================================================================
    event_triggered = QtCore.Signal(QtCore.QObject, QtCore.QEvent)

    # =====================================================================
    # +++ CONSTRUCTOR
    # =====================================================================
    def __init__(self, parent=None):
        super(VisualTreeEventFilter, self).__init__(parent)

    # =====================================================================
    # +++ OVERRIDES
    # =====================================================================
    def eventFilter(self, obj, event):
        self.event_triggered.emit(obj, event)
        return False


# *********************************************************************
# +++ CLASSES
# *********************************************************************
class VisualTreeDebugger(QtWidgets.QWidget):
    # =====================================================================
    # +++ CONSTRUCTOR
    # =====================================================================
    def __init__(self, parent=None, compiler_type=None):
        super(VisualTreeDebugger, self).__init__(parent)
        # -- Compiler
        self._compiler_type = compiler_type if compiler_type else VisualCompilerDefault

        # -- Explorer
        self._explorer = VisualTreeExplorer()
        self._explorer.selection_changed.connect(self._selection_changed)
        self._explorer.update_style_requested.connect(self._update_style)
        self._explorer.closing.connect(self._save_settings)
        self._explorer.show()

        self._explorer.update_tree(parent)

        self._file_watch_timer = QtCore.QTimer(self)
        self._file_watch_timer.timeout.connect(self._update_monitor)
        self._file_watch_timer.start(500)

        self._css_last_mod_time = None
        self._vars_last_mod_time = None

        QtCore.QTimer.singleShot(0, self._update_explorer_geometry)

        # -- Painter
        self._painter = VisualTreePainter(parent)

        # -- Event Filter
        self._event_filter = VisualTreeEventFilter(self)
        self._event_filter.event_triggered.connect(self._event_triggered)
        self.parent().installEventFilter(self._event_filter)

        # -- Settings
        parent_application_name = QtCore.QCoreApplication.applicationName()
        self._settings = QtCore.QSettings('qssDebugger', parent_application_name)
        self._load_settings()

    # ====================================================================
    # +++ PRIVATE METHODS
    # =====================================================================
    def _load_settings(self):
        self._explorer.watch_css_folder_path = self._settings.value('watch_css_path')
        self._explorer.watch_vars_folder_path = self._settings.value('watch_vars_path')
        self._explorer.compiled_file_path = self._settings.value('compiled_css_path')

    def _save_settings(self):
        if self._explorer.is_settings_valid:
            self._settings.setValue('watch_css_path', self._explorer.watch_css_folder_path)
            self._settings.setValue('watch_vars_path', self._explorer.watch_vars_folder_path)
            self._settings.setValue('compiled_css_path', self._explorer.compiled_file_path)

    def _update_style(self, style_file_path=None):
        if not style_file_path:
            style_file_path = self._explorer.compiled_file_path

        with open(style_file_path, 'r') as file_handle:
            result = file_handle.read()

        self.parent().setStyleSheet(result)

    def _update_monitor(self):
        if self._explorer.is_settings_valid:

            if not self._css_last_mod_time:
                self._css_last_mod_time = os.path.getmtime(self._explorer.watch_css_folder_path)

            if not self._vars_last_mod_time:
                self._vars_last_mod_time = os.path.getmtime(self._explorer.watch_vars_folder_path)

            css_current_mod_time = os.path.getmtime(self._explorer.watch_css_folder_path)
            vars_current_mod_time = os.path.getmtime(self._explorer.watch_vars_folder_path)

            if self._css_last_mod_time != css_current_mod_time or \
               self._vars_last_mod_time != vars_current_mod_time:

                self._explorer.log_message('Change detected, compiling...')
                self._css_last_mod_time = None
                self._vars_last_mod_time = None

                self._compiler_type.compile(self._explorer.watch_css_folder_path,
                                            self._explorer.watch_vars_folder_path,
                                            self._explorer.compiled_file_path)

                self._update_style(self._explorer.compiled_file_path)
                self._explorer.log_message('...done.')

    def _update_explorer_geometry(self):
        explorer_x = self.parent().geometry().x() + self.parent().geometry().width() + 12
        explorer_y = self.parent().geometry().y()
        explorer_width = self._explorer.geometry().width()
        explorer_height = self.parent().geometry().height()
        self._explorer.setGeometry(explorer_x, explorer_y, explorer_width, explorer_height)

    def _event_triggered(self, obj, event):
        if event.type() in [QtCore.QEvent.Move, QtCore.QEvent.Resize]:
            self._update_explorer_geometry()

        elif event.type() == QtCore.QEvent.KeyPress and event.key() == QtCore.Qt.Key_Insert:
            mouse_pos = QtGui.QCursor.pos()
            mouse_pos = self.parent().mapFromGlobal(mouse_pos)
            visual_item_hit = self.parent().childAt(mouse_pos)

            if visual_item_hit:
                self._explorer.set_selected_item(visual_item_hit)

    # ====================================================================
    # +++ CALLBACKS
    # =====================================================================
    def _selection_changed(self, visual_items):
        self._painter.current_items = visual_items


# ********************************************************************
# +++ TESTING
# *********************************************************************
if __name__ == "__main__":

    # Main testing window class
    class Window(QtWidgets.QMainWindow):
        def __init__(self):
            super(Window, self).__init__(None)

            dummy_lyt = QtWidgets.QVBoxLayout()

            dummy_lyt.addWidget(QtWidgets.QPushButton('Button'))
            dummy_lyt.addWidget(QtWidgets.QLabel('Button'))
            dummy_lyt.addWidget(QtWidgets.QCheckBox('Button'))

            dummy_wgt = QtWidgets.QWidget()
            dummy_wgt.setLayout(dummy_lyt)

            self.setCentralWidget(dummy_wgt)

    app = QtWidgets.QApplication([])
    window = Window()

    # Attach debugger
    debugger = VisualTreeDebugger(window)

    window.show()
    app.exec_()
