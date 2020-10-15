"""
        Physics Department at Federal University of Pernambuco, Recife-PE, Brazil.
                                Nano-Optics Laboratory
                            Heating Device - User Interface

                                Recife-Pernambuco, Brazil
                                        September 2020

Allison Pessoa
allisonpessoa@hotmail.com
"""

#System
import sys
import os.path
import time
#Interface
from PyQt5 import QtCore, QtGui, QtWidgets, uic
layout_form = uic.loadUiType("layout.ui")[0]
#CurvePlot
from guiqwt.plot import CurveWidget
from guiqwt.builder import make
#Dialogs
sys.path.append(os.path.abspath("dialogs"))
import settings_dialog
import help_dialog
from errorbox import errorBoxAlternative
#USB communication
import serial
from serial.tools import list_ports
#Others
import pickle
import numpy as np

class Plot():
    def __init__(self, widget_plot, toolbar):
        self.widget_plot = widget_plot
        self.toolbar = toolbar
        self.data =  [0,1] #Initial data, arbitrary
        #Curve widget
        self.plotWidget = CurveWidget(self.widget_plot, xlabel=('Time'),
                                                ylabel=('Temperature'), xunit=('min'),
                                                yunit=('°C'))
        #self.plotWidget.add_toolbar(self.toolbar, "default") #Removed ToolBar in this version for now
        #self.plotWidget.register_all_curve_tools()
        #Curve item
        self.item = make.curve(np.asarray(range(len(self.data))),np.asarray(self.data))
        #Curve plot
        self.plot = self.plotWidget.get_plot()
        self.plot.add_item(self.item)
        self.plotWidget.resize(self.widget_plot.size())
        self.plotWidget.show()

    def setData(self, data):
        self.item.set_data(np.asarray(data[0]),np.asarray(data[1]))
        self.plot.do_autoscale()
        self.plot.replot()

class Worker(QtCore.QObject):
    #Attributes
    parent = None
    paired = False
    ser = None
    #Signals
    atualizeListPorts = QtCore.pyqtSignal(list)
    atualizeData = QtCore.pyqtSignal(float)
    emitError = QtCore.pyqtSignal(str)

    def loopWork(self):
        while 1:
            if self.paired == False:
                self.atualizeListPorts.emit(serial.tools.list_ports.comports())
            else:
                self.acquire()

    def setPoint(self, tempValue):#avoid access objects direct from Main
        try:
            text = str("SETPT("+str(int(tempValue*10))+")").encode('utf-8') #x10 to increase precision
            self.ser.write(text)
        except Exception as erro:
            errorMessage = erro.args[0]
            self.emitError.emit(errorMessage)

    def updateSettings(self, control_P, control_I, control_D):
        try:
            self.ser.write(str("UPDSETT("+str(int(control_P))+","+str(int(control_I))+","+str(int(control_D))+")").encode('utf-8'))
        except Exception as erro:
            errorMessage = erro.args[0]
            self.emitError.emit(errorMessage)

    def acquire(self):
        value = 0
        try:
            receivedData = self.ser.readline()
            self.ser.flush()
            self.entryLine = receivedData.decode('utf-8')
            if self.entryLine != "":
                if self.entryLine[0] == 'A':#First Character is always A.
                    value = float(self.entryLine[1:])
                    self.atualizeData.emit(value)

        except Exception as erro:
            errorMessage = erro.args[0]
            self.emitError.emit(errorMessage)

class Main(QtWidgets.QMainWindow, layout_form):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self,parent)
        self.setupUi(self)
        ##### INITIAL PROPERTIES #####
        self.minTemp = 20
        self.maxTemp = 80
        self.control_P = 100
        self.control_I = 10
        self.control_D = 1

        self.setPoint = 20
        self.tempList = []
        self.elapsedTime = []
        #Serial Related
        self.boudRate = 9600
        self.listPorts = serial.tools.list_ports.comports()
        for i in range(len(self.listPorts)):
            self.comboBox_serialPort.addItem(self.listPorts[i].description, self.listPorts[i].name)
        #Plot
        self.mainToolbar = self.addToolBar("Plot")
        self.plot = Plot(self.widget_plot, self.mainToolbar)
        #Settings Dialog
        self.settingsDlg = settings_dialog.settings_dialog(self)
        self.settingsDlg.Ok.connect(self.updateSettings)
        self.helpDlg = help_dialog.help_dialog(self)
        ##### WIDGET ACTIONS #####
        #~Buttons
        self.pushButton_pair.clicked.connect(self.pair_unpair)
        self.pushButton_clearPlot.clicked.connect(self.clearPlot)
        self.pushButton_settings.clicked.connect(self.openSettingsDialog)
        self.pushButton_help.clicked.connect(self.openHelpDialog)
        self.pushButton_set.clicked.connect(self.changeTemp)
        #~ComboBox
        self.comboBox_serialPort.activated.connect(self.selecDevice)
        ##### THREADS SETTINGS #####
        #Initial Settings
        self.routine = Worker()
        self.routine.parent = self
        self.executionThread = QtCore.QThread()
        self.routine.moveToThread(self.executionThread)
        self.executionThread.started.connect(self.routine.loopWork)
        self.executionThread.start()
        #Thread Signals
        self.routine.atualizeListPorts.connect(self.updateListPorts)
        self.routine.atualizeData.connect(self.atualizeData)
        self.routine.emitError.connect(self.errorBoxShow)

    ##### FUNCTIONS #####
    ##INTERFACE
    def clearPlot(self):
        self.tempList.clear()
        self.initTime = time.localtime().tm_min + time.localtime().tm_sec/60
        self.elapsedTime.clear()
        self.plot.setData(([],[]))

    def selecDevice(self):
        self.pushButton_pair.setDisabled(False)

    def openSettingsDialog(self):
        self.settingsDlg.exec_()

    def openHelpDialog(self):
        self.helpDlg.exec_()

    def errorBoxShow(self, string):
        errorBoxAlternative(string)

    def atualizeData(self, value):
        self.lcdNumber_actTemp.display(value)
        self.tempList.append(value)

        self.currentTime = time.localtime().tm_min + time.localtime().tm_sec/60
        self.elapsedTime.append(abs(self.currentTime-self.initTime))

        self.plot.setData((self.elapsedTime, self.tempList))#ALT: Não sei se vai funcionar, passar uma string...
        self.progressBar.setValue(100*(self.tempList[-1]-self.minTemp)/(self.maxTemp - self.minTemp))

    def changeTemp(self):
        self.routine.ser.reset_input_buffer()
        self.routine.ser.reset_output_buffer()
        time.sleep(0.5)

        self.setPoint = self.doubleSpinBox_setPoint.value()
        self.routine.setPoint(self.setPoint)
        time.sleep(0.5)

    def updateSettings(self):
        self.minTemp = self.settingsDlg.parameters["spinBox_min"]
        self.maxTemp = self.settingsDlg.parameters["spinBox_max"]
        self.control_P = self.settingsDlg.parameters["spinBox_P"]
        self.control_I = self.settingsDlg.parameters["spinBox_I"]
        self.control_D = self.settingsDlg.parameters["spinBox_D"]
        self.doubleSpinBox_setPoint.setMinimum(self.minTemp)
        self.doubleSpinBox_setPoint.setMaximum(self.maxTemp)

        try:
            self.routine.updateSettings(self.control_P,self.control_I,self.control_D)
            time.sleep(0.5)
            self.statusBar().showMessage("Settings updated successfully")
        except Exception as erro:
            errorMessage =  erro.args[0]
            errorBoxAlternative(errorMessage + ". Certify you are connected to Device")
            self.statusBar().showMessage("Settings not updated")


    #SERIAL USB COMMUNICATION
    def pair_unpair(self):
        #conectar ou desconectar, dependendo do estado do botão
        if  self.pushButton_pair.isChecked() == True:
            if self.comboBox_serialPort.currentText() != 'None':
                portIndex = self.comboBox_serialPort.currentIndex()
                self.boudRate = self.spinBox_boudRate.value()
                try:
                    self.routine.ser = serial.Serial(self.listPorts[portIndex].device, self.boudRate, timeout=10, write_timeout=10)
                    self.routine.paired = True

                    self.clearPlot()
                    self.updateSettings() #Update PID params
                    time.sleep(0.5)

                    self.statusBar().showMessage("Device paired successfully")
                    self.pushButton_pair.setText("Unpair")
                    self.doubleSpinBox_setPoint.setDisabled(False)
                    self.pushButton_set.setDisabled(False)

                except Exception as erro:
                    self.pushButton_pair.setChecked(False)
                    errorMessage =  erro.args[0]
                    errorBoxAlternative(errorMessage)
        else:
            self.finishUnpair()

    def finishUnpair(self):
        self.routine.setPoint(20)#Security Setpoint after finish
        time.sleep(0.3)

        self.routine.paired = False
        time.sleep(0.3)
        self.routine.ser.close()

        self.statusBar().showMessage("Device unpaired")
        self.pushButton_pair.setText("Pair")
        self.doubleSpinBox_setPoint.setDisabled(True)
        self.pushButton_set.setDisabled(True)

    def updateListPorts(self, newListPorts):
        if self.listPorts != newListPorts:
            self.listPorts = newListPorts
            self.comboBox_serialPort.clear()
            for i in range(len(self.listPorts)):
                self.comboBox_serialPort.addItem(self.listPorts[i].description)
        else:
            pass

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Main()
    window.show()
    app.exec_()
