"""
DialogBox oppened by the Main User Interface. Contains parameters set by users.
"""

import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import pickle
import os.path

layout_form_settings = uic.loadUiType("dialogs/settings_dialog.ui")[0]

class settings_dialog(QtWidgets.QDialog, layout_form_settings):
    Ok = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self,parent)
        self.setupUi(self)
        self.loadInfo()

        self.pushButton_ok.clicked.connect(self.okPushButton)
        self.pushButton_cancel.clicked.connect(self.cancelPushButton)

        self.spinBox_minTemp.valueChanged.connect(self.actualizeLimits)
        self.spinBox_maxTemp.valueChanged.connect(self.actualizeLimits)

    def actualizeLimits(self):
        self.spinBox_minTemp.setMaximum(self.spinBox_maxTemp.value())
        self.spinBox_maxTemp.setMinimum(self.spinBox_minTemp.value())

    def okPushButton(self):
        self.saveInfo()
        self.Ok.emit()
        self.close()

    def cancelPushButton(self):
        self.close()

    def saveInfo(self):
        self.parameters = {
            "spinBox_min": self.spinBox_minTemp.value(),
            "spinBox_max": self.spinBox_maxTemp.value(),
            "spinBox_P": self.spinBox_P.value(),
	        "spinBox_I": self.spinBox_I.value(),
	        "spinBox_D": self.spinBox_D.value(),
        }
        filename = 'dialogs/settings.plk'
        try:
            file = open(filename, 'wb')
            pickle.dump(self.parameters, file)
            file.close()
        except:
            QtWidgets.QErrorMessage().showMessage('Error on saving file')

    def loadInfo(self):
        if (os.path.isfile("dialogs/settings.plk")):
            filename = 'dialogs/settings.plk'
            try:
                file = open(filename, 'rb')
                self.parameters = pickle.load(file)
                file.close()

                self.spinBox_minTemp.setValue(self.parameters["spinBox_min"])
                self.spinBox_maxTemp.setValue(self.parameters["spinBox_max"])
                self.spinBox_P.setValue(self.parameters["spinBox_P"])
                self.spinBox_I.setValue(self.parameters["spinBox_I"])
                self.spinBox_D.setValue(self.parameters["spinBox_D"])
            except:
                QtWidgets.QErrorMessage().showMessage('Error on oppening file')

        else:
            self.saveInfo()
