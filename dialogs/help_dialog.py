"""
DialogBox oppened by the Main User Interface. Help information.
"""

import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic

layout_form_help = uic.loadUiType("dialogs/help_dialog.ui")[0]

class help_dialog(QtWidgets.QDialog, layout_form_help):
    Ok = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self,parent)
        self.setupUi(self)
