# --- references ---
# 1) https://zetcode.com/gui/pyqt5/layout/ for layout
# 2) https://www.learnpyqt.com/tutorials/plotting-pyqtgraph/ for graph
# 3) https://www.youtube.com/watch?v=09pY6IkwWMs&ab_channel=MarkWinfield file save

import sys
import pyqtgraph as pg
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QThread, QObject, pyqtSignal
from PyQt5.QtWidgets import (QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QApplication, QLabel, QLineEdit,
                             QGridLayout, QComboBox)
import heartpy as hp
import numpy as np
from random import randint
import serial


class GetData:

    def __init__(self):
        super().__init__()
        # data_source = serial.Serial("COM7", 115200)
        # for i in range(10):
        # data_source.readline()
        pass

    def get_time_and_data(self):
        data_packet = "red: 1 ir: 2 hr: 3 spo2: 4 3 4 5 6 7 8 9 10 11"
        data_packet = data_packet.rstrip()
        reading = data_packet.split(" ")
        data = {"red": -float(reading[1]),
                "ir": -float(reading[3]),
                "hr": float(reading[5]),
                "spo2": float(reading[7]),
                "acc_x": float(reading[8]),
                "acc_y": float(reading[9]),
                "acc_z": float(reading[10]),
                "mag_x": float(reading[11]),
                "mag_y": float(reading[12]),
                "mag_z": float(reading[13]),
                "gyr_x": float(reading[14]),
                "gyr_y": float(reading[15]),
                "gyr_z": float(reading[16])
                }
        return data


class MainPage(QWidget):

    def __init__(self):
        super().__init__()
        self.x = list(range(100))
        self.redData = [0] * 100
        self.irData = [0] * 100
        self.hrData = [0] * 100
        self.spo2Data = [0] * 100
        self.accXData = [0] * 100
        self.accYData = [0] * 100
        self.accZData = [0] * 100
        self.magXData = [0] * 100
        self.magYData = [0] * 100
        self.magZData = [0] * 100
        self.gyrXData = [0] * 100
        self.gyrYData = [0] * 100
        self.gyrZData = [0] * 100
        self.initUI()

    def update_plot_data(self):
        if not self.load:
            data = GetData2.get_time_and_data(self)
            self.redData.append(data["red"])
            self.irData.append(data["ir"])
            self.hrData.append(data["hr"])
            self.spo2Data.append(data["spo2"])
            self.accXData.append(data["acc_x"])
            self.accYData.append(data["acc_y"])
            self.accZData.append(data["acc_z"])
            self.magXData.append(data["mag_x"])
            self.magYData.append(data["mag_y"])
            self.magZData.append(data["mag_z"])
            self.gyrXData.append(data["gyr_x"])
            self.gyrYData.append(data["gyr_y"])
            self.gyrZData.append(data["gyr_z"])
            self.x = self.x[1:]
            self.x.append(self.x[-1] + 1)
            self.dataline1.setData(self.x, self.redData[-100:])
            self.dataline2.setData(self.x, self.irData[-100:])
            self.dataline3.setData(self.x, self.hrData[-100:])
            self.dataline4.setData(self.x, self.spo2Data[-100:])
            self.imuline1x.setData(self.x, self.accXData[-100:])
            self.imuline1y.setData(self.x, self.accYData[-100:])
            self.imuline1z.setData(self.x, self.accZData[-100:])
            self.imuline2x.setData(self.x, self.magXData[-100:])
            self.imuline2y.setData(self.x, self.magYData[-100:])
            self.imuline2z.setData(self.x, self.magZData[-100:])
            self.imuline3x.setData(self.x, self.gyrXData[-100:])
            self.imuline3y.setData(self.x, self.gyrYData[-100:])
            self.imuline3z.setData(self.x, self.gyrZData[-100:])

            if self.x[0] % 50 == 0:
                self.currentRR.setText(str(self.calculate_RR()))

    def calculate_RR(self):
        irArray = np.array(self.irData[-200:])
        irArray = irArray - min(irArray)
        wd, m = hp.process(irArray, 25)
        m, wd = hp.analysis.calc_breathing(wd['RR_list_cor'], measures=m, working_data=wd)
        breaths = 60 * m['breathingrate']
        return round(breaths,1)

    def start_record(self):
        self.position = len(self.redData) - 1
        print(self.position)

    def file_save(self):
        subject = self.subjectEdit.text()
        age = self.ageEdit.text()
        gender = self.genderEdit.text()
        weight = self.weightEdit.text()
        height = self.heightEdit.text()
        defaultname = subject + "_" + age + "_" + gender + "_" + weight + "_" + height + '.csv'
        name = QtGui.QFileDialog.getSaveFileName(self, 'Save File', 'C:/Users/Kim/Desktop/ureca/march/' + defaultname)
        if len(name[0]) > 0:
            file = open(name[0], 'w')
            file.write("redData,irData,hrData(bpm),spo2Data(%),accX,accY,accZ,magX,magY,magZ,gyrX,gyrY,gyrZ\n")
            for i in range(self.position, len(self.redData)):
                text = str(self.redData[i]) + ',' + str(self.irData[i]) + ',' + str(self.hrData[i]) + ',' + str(
                    self.spo2Data[i]) + ',' + str(self.accXData[i]) + ',' + str(self.accYData[i]) + ',' + str(
                    self.accZData[i]) + ',' + str(self.magXData[i]) + ',' + str(self.magYData[i]) + ',' + str(
                    self.magZData[i]) + ',' + str(self.gyrXData[i]) + ',' + str(self.gyrYData[i]) + ',' + str(
                    self.gyrZData[i]) + '\n'
                file.write(text)
            file.close()

    def live_data(self):
        self.load = False
        self.position = 0
        self.redData = [0] * 100
        self.irData = [0] * 100
        self.hrData = [0] * 100
        self.spo2Data = [0] * 100
        self.accXData = [0] * 100
        self.accYData = [0] * 100
        self.accZData = [0] * 100
        self.magXData = [0] * 100
        self.magYData = [0] * 100
        self.magZData = [0] * 100
        self.gyrXData = [0] * 100
        self.gyrYData = [0] * 100
        self.gyrZData = [0] * 100

    def file_load(self):
        self.load = True
        name = QtGui.QFileDialog.getOpenFileName(self, 'Open File', 'C:/Users/Kim/Desktop/ureca/march/', 'CSV (*.csv)')
        if len(name[0]) > 0:
            file = open(name[0], 'r')
            file.readline()
            self.redData = []
            self.irData = []
            self.hrData = []
            self.spo2Data = []
            self.accXData = []
            self.accYData = []
            self.accZData = []
            self.magXData = []
            self.magYData = []
            self.magZData = []
            self.gyrXData = []
            self.gyrYData = []
            self.gyrZData = []
            for l in file:
                s = l.split(',')
                self.redData.append(-float(s[0]))
                self.irData.append(-float(s[1]))
                self.hrData.append(float(s[2]))
                self.spo2Data.append(float(s[3]))
                self.accXData.append(float(s[4]))
                self.accYData.append(float(s[5]))
                self.accZData.append(float(s[6]))
                self.magXData.append(float(s[7]))
                self.magYData.append(float(s[8]))
                self.magZData.append(float(s[9]))
                self.gyrXData.append(float(s[10]))
                self.gyrYData.append(float(s[11]))
                self.gyrZData.append(float(s[12]))
            file.close()
        self.dataline1.setData(self.redData)
        self.dataline2.setData(self.irData)
        self.dataline3.setData(self.hrData)
        self.dataline4.setData(self.spo2Data)
        self.imuline1x.setData(self.accXData)
        self.imuline1y.setData(self.accYData)
        self.imuline1z.setData(self.accZData)
        self.imuline2x.setData(self.magXData)
        self.imuline2y.setData(self.magYData)
        self.imuline2z.setData(self.magZData)
        self.imuline3x.setData(self.gyrXData)
        self.imuline3y.setData(self.gyrYData)
        self.imuline3z.setData(self.gyrZData)

    def initUI(self):
        self.position = 0
        self.load = False
        self.setStyleSheet('font-size: 11pt; font-family: Consolas')
        bottombox = QHBoxLayout()
        bottombox.addLayout(self.ui_column1(), 2)
        bottombox.addLayout(self.ui_column2(), 2)
        bottombox.addLayout(self.ui_column3(), 1)
        vbox = QVBoxLayout()
        vbox.addLayout(self.ui_topbar())
        vbox.addLayout(bottombox)
        vbox.addStretch(1)
        self.setLayout(vbox)
        self.setGeometry(300, 60, 1200, 900)
        self.setWindowTitle('Data collection window')
        self.setWindowIcon(QtGui.QIcon('heart.png'))
        self.show()

    def ui_topbar(self):
        portLabel = QLabel("Port")
        portChoice = QComboBox()
        portChoice.addItems(["COM7", "COM8", "COM9"])
        recordButton = QPushButton("Start recording")
        recordButton.clicked.connect(self.start_record)
        saveButton = QPushButton("Save file as")
        saveButton.clicked.connect(self.file_save)
        loadButton = QPushButton("Load file")
        loadButton.clicked.connect(self.file_load)
        liveButton = QPushButton("Live data")
        liveButton.clicked.connect(self.live_data)

        topbox = QHBoxLayout()
        topbox.addWidget(portLabel)
        topbox.addWidget(portChoice)
        topbox.addWidget(recordButton)
        topbox.addWidget(saveButton)
        topbox.addWidget(loadButton)
        topbox.addWidget(liveButton)
        topbox.addStretch(1)
        return topbox

    def ui_column1(self):
        column1 = QVBoxLayout()
        heading1 = QLabel("First column")
        heading1.setFont(QtGui.QFont("Consolas", 15, QtGui.QFont.Bold))
        column1.addWidget(heading1)

        column1.addWidget(QLabel("PPG Signal (Red)"))
        graph1 = pg.PlotWidget(labels = {'left' : 'Detected intensity (a.u.)', 'bottom': 'Data point'})
        graph1.setBackground("w")
        pen = pg.mkPen(color=(255, 0, 0))
        self.dataline1 = graph1.plot(self.redData, pen=pen)
        column1.addWidget(graph1)

        column1.addWidget(QLabel("PPG Signal (IR)"))
        graph2 = pg.PlotWidget(labels = {'left' : 'Detected intensity (a.u)', 'bottom': 'Data point'})
        graph2.setBackground("w")
        pen = pg.mkPen(color=(255, 0, 0))
        self.dataline2 = graph2.plot(self.irData, pen=pen)
        column1.addWidget(graph2)

        column1.addWidget(QLabel("Heart Rate (bpm)"))
        graph3 = pg.PlotWidget(labels = {'left' : 'Heart Rate (bpm)', 'bottom': 'Data point'})
        graph3.setYRange(50, 120, padding=0)
        graph3.setBackground("w")
        pen = pg.mkPen(color=(255, 0, 0))
        self.dataline3 = graph3.plot(self.hrData, pen=pen)
        column1.addWidget(graph3)

        column1.addWidget(QLabel("SpO2 (%)"))
        graph4 = pg.PlotWidget(labels = {'left' : 'SpO2 (%)', 'bottom': 'Data point'})
        graph4.setYRange(80, 100, padding=0)
        graph4.setBackground("w")
        pen = pg.mkPen(color=(255, 0, 0))
        self.dataline4 = graph4.plot(self.spo2Data, pen=pen)
        self.timer = QtCore.QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()
        column1.addWidget(graph4)
        column1.addStretch(1)
        return column1

    def ui_column2(self):
        column2 = QVBoxLayout()
        heading2 = QLabel("Second column")
        heading2.setFont(QtGui.QFont("Consolas", 15, QtGui.QFont.Bold))
        column2.addWidget(heading2)

        column2.addWidget(QLabel("IMUa Signals"))
        imugraph1 = pg.PlotWidget(labels = {'left' : 'Linear Acceleration (ms^-2)', 'bottom': 'Data point'})
        imugraph1.setBackground("w")
        imugraph1.addLegend(offset = (0,0))
        pen = pg.mkPen(color=(255, 0, 0))
        self.imuline1x = imugraph1.plot(self.x, self.accXData, pen=pen, name = "x-axis")
        pen = pg.mkPen(color=(0, 255, 0))
        self.imuline1y = imugraph1.plot(self.x, self.accYData, pen=pen, name = "y-axis")
        pen = pg.mkPen(color=(0, 0, 255))
        self.imuline1z = imugraph1.plot(self.x, self.accZData, pen=pen, name = "z-axis")
        column2.addWidget(imugraph1)

        column2.addWidget(QLabel("IMUm Signals"))
        imugraph2 = pg.PlotWidget(labels = {'left' : 'Magnetic Field Strength (µT)', 'bottom': 'Data point'})
        imugraph2.setBackground("w")
        imugraph2.addLegend(offset=(0, 0))
        pen = pg.mkPen(color=(255, 0, 0))
        self.imuline2x = imugraph2.plot(self.x, self.magXData, pen=pen, name = "x-axis")
        pen = pg.mkPen(color=(0, 255, 0))
        self.imuline2y = imugraph2.plot(self.x, self.magYData, pen=pen, name = "y-axis")
        pen = pg.mkPen(color=(0, 0, 255))
        self.imuline2z = imugraph2.plot(self.x, self.magZData, pen=pen, name = "z-axis")
        column2.addWidget(imugraph2)

        column2.addWidget(QLabel("IMUg Signals"))
        imugraph3 = pg.PlotWidget(labels = {'left' : 'Angular Rate (Dps)', 'bottom': 'Data point'})
        imugraph3.setBackground("w")
        imugraph3.addLegend(offset=(0, 0))
        pen = pg.mkPen(color=(255, 0, 0))
        self.imuline3x = imugraph3.plot(self.x, self.gyrXData, pen=pen, name = "x-axis")
        pen = pg.mkPen(color=(0, 255, 0))
        self.imuline3y = imugraph3.plot(self.x, self.gyrYData, pen=pen, name = "y-axis")
        pen = pg.mkPen(color=(0, 0, 255))
        self.imuline3z = imugraph3.plot(self.x, self.gyrZData, pen=pen, name = "z-axis")
        column2.addWidget(imugraph3)

        column2.addStretch(1)
        return column2

    def ui_column3(self):
        column3 = QVBoxLayout()
        heading3 = QLabel("Details")
        heading3.setFont(QtGui.QFont("Consolas", 15, QtGui.QFont.Bold))
        column3.addWidget(heading3)

        subject = QLabel("Subject")
        age = QLabel("Age")
        gender = QLabel("Gender")
        weight = QLabel("Weight")
        height = QLabel("Height")
        blank = QLabel("")
        rr = QLabel("Respiratory\nrate (bpm)")
        self.currentRR = QLabel("Processing...")

        self.subjectEdit = QLineEdit()
        self.ageEdit = QLineEdit()
        self.genderEdit = QLineEdit()
        self.weightEdit = QLineEdit()
        self.heightEdit = QLineEdit()

        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(subject, 1, 0)
        grid.addWidget(self.subjectEdit, 1, 1)
        grid.addWidget(age, 2, 0)
        grid.addWidget(self.ageEdit, 2, 1)
        grid.addWidget(gender, 3, 0)
        grid.addWidget(self.genderEdit, 3, 1)
        grid.addWidget(weight, 4, 0)
        grid.addWidget(self.weightEdit, 4, 1)
        grid.addWidget(height, 5, 0)
        grid.addWidget(self.heightEdit, 5, 1)
        grid.addWidget(blank, 6, 0)
        grid.addWidget(rr, 8, 0)
        grid.addWidget(self.currentRR, 8, 1)
        column3.addLayout(grid)
        column3.addStretch(1)
        return column3


def main():
    app = QApplication(sys.argv)
    example = MainPage()
    sys.exit(app.exec_())


if __name__ == '__main__':
    GetData2 = GetData
    main()
