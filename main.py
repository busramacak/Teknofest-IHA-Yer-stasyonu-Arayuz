import serial
from PyQt5.QtCore import QThread
from PyQt5.QtSerialPort import QSerialPortInfo
from PyQt5.QtWidgets import QFrame, QVBoxLayout
from pyqtgraph import PlotWidget
from collections import deque
import pyqtgraph as pg
from PyQt5 import QtWidgets
from PyQt5 import QtCore, QtGui
from qtpy.QtCore import Qt
from qtpy.QtGui import QPainter, QPen, QPixmap, QFont
from qtpy.QtWidgets import QGraphicsView, QGraphicsItem
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from pytilemap import MapGraphicsView, MapTileSourceHere
import csv
import vtk

veri_liste = list()
gpsLatitude = list()
gpsLongitude = list()

#TELEMETRİ KAYIT YOLU
konum ="C:\\Users\\Busra\\Desktop\\Telemetri Paketi.csv"
#SERİ PORT SEÇİM
portName = "COM5"
seri = serial.Serial()

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1910, 990)
        MainWindow.setStyleSheet("")
        MainWindow.showMaximized()

        self.currentSTL = None
        self.lastDir = None
        self.droppedFilename = None

        self.grafikZamanlayıcı = None
        self.grafikZamanlayıcı1 = None
        self.time = 0

        self.time_kuyruk = deque([], maxlen=20)
        self.timeaxis = []
        self.cizgi = dict()
        self.cizgi1 = dict()
        self.cizgi2 = dict()
        self.cizgi3 = dict()

        self._pointText = {0: "N", 45: "NE", 90: "E", 135: "SE", 180: "S", 225: "SW", 270: "W", 315: "NW"}

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setStyleSheet("background-color: #e6e7e8;")
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setAlignment(QtCore.Qt.AlignCenter)
        self.progressBar.setGeometry(QtCore.QRect(900, 910, 270, 71))
        self.progressBar.setValue(90)
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setStyleSheet("""
                            QProgressBar{
                                border: 1px solid grey;
                                border-radius: 5px;
                                text-align: center;
                                font: 10pt Arial;
                            }

                            QProgressBar::chunk {
                                background-color: #9cd9ff;
                                width: 10px;
                                margin: 1px;
                            }
                            """)
        self.baglanButon = QtWidgets.QPushButton(self.centralwidget)
        self.baglanButon.setGeometry(QtCore.QRect(10, 910, 211, 71))
        self.baglanButon.setObjectName("baglanButon")
        self.baglanButon.clicked.connect(self.baglanClick)
        self.baglanButon.setStyleSheet("""
                            QPushButton{
                                border-radius: 10px;
                                background-color : #6799b8;
                                font: 9pt Calibri Light;
                            }
                            QPushButton::hover
                            {
                                border : 0.5px solid grey;
                                background-color : #9cd9ff;
                            }""")


        ########################################################################################################################

        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 1911, 791))
        self.tabWidget.setObjectName("tabWidget")

        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.tab.setStyleSheet("background-color: #e6e7e8;")
        self.tabWidget.addTab(self.tab, "")

        styles = {'color': 'b', 'font-size': '14px'}
        self.yukseklikGrafik = PlotWidget(self.tab)
        self.yukseklikGrafik.setGeometry(QtCore.QRect(10, 10, 441, 351))
        self.yukseklikGrafik.setObjectName("yukseklikGrafik")
        self.yukseklikGrafik.setBackground('w')
        x1 = self.yukseklikGrafik.getAxis('bottom')
        x1.setLabel(text='Zaman(s)', **styles)
        y1 = self.yukseklikGrafik.getAxis('left')
        y1.setLabel(text='Yükseklik (m)', **styles)
        self.yukseklikGrafik.showGrid(x=True, y=True)
        self.sicaklikGrafik = PlotWidget(self.tab)
        self.sicaklikGrafik.setGeometry(QtCore.QRect(470, 10, 441, 351))
        self.sicaklikGrafik.setObjectName("sicaklikGrafik")
        self.sicaklikGrafik.setBackground('w')
        x2 = self.sicaklikGrafik.getAxis("bottom")
        x2.setLabel(text='Zaman (s)', **styles)
        y2 = self.sicaklikGrafik.getAxis('left')
        y2.setLabel(text='Sıcaklık (°C)', **styles)
        self.sicaklikGrafik.showGrid(x=True, y=True)
        self.basincGrafik = PlotWidget(self.tab)
        self.basincGrafik.setGeometry(QtCore.QRect(10, 380, 441, 351))
        self.basincGrafik.setObjectName("basincGrafik")
        self.basincGrafik.setBackground('w')
        x3 = self.basincGrafik.getAxis("bottom")
        x3.setLabel(text='Zaman (s)', **styles)
        y3 = self.basincGrafik.getAxis('left')
        y3.setLabel(text='Basınç (pa)', **styles)
        self.basincGrafik.showGrid(x=True, y=True)
        self.inisHiziGrafik = PlotWidget(self.tab)
        self.inisHiziGrafik.setGeometry(QtCore.QRect(470, 380, 441, 351))
        self.inisHiziGrafik.setObjectName("inisHiziGrafik")
        self.inisHiziGrafik.setBackground("w")
        x4 = self.inisHiziGrafik.getAxis("bottom")
        x4.setLabel(text='Zaman (s)', **styles)
        y4 = self.inisHiziGrafik.getAxis('left')
        y4.setLabel(text='İniş Hızı (m/s)', **styles)
        self.inisHiziGrafik.showGrid(x=True, y=True)
        self.yukseklikmax = deque([], maxlen=20)
        self.sicaklikmax = deque([], maxlen=20)
        self.basincmax = deque([], maxlen=20)
        self.inisHizimax = deque([], maxlen=20)

        #############################################################################

        self.haritaWidget = QtWidgets.QWidget(self.tab)
        self.haritaWidget.setGeometry(QtCore.QRect(930, 10, 951, 741))
        self.haritaWidget.setObjectName("haritaWidget")
        self.vertical = QtWidgets.QVBoxLayout(self.haritaWidget)
        self.vertical.setContentsMargins(0, 0, 0, 0)
        self.vertical.setObjectName("vertical")
        self.view = MapGraphicsView(tileSource=MapTileSourceHere())
        #yarışma alanının konumları girilecek.(longitutde,latitude)
        self.view.scene().setCenter(31.7565452, 41.4494227)
        self.view.setOptimizationFlag(QGraphicsView.DontSavePainterState, True)
        self.view.setRenderHint(QPainter.Antialiasing, True)
        self.view.setRenderHint(QPainter.SmoothPixmapTransform, True)
        self.vertical.addWidget(self.view)

        ########################################################################################################################
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tab_2.setStyleSheet("background-color: #e6e7e8;")
        self.tabWidget.addTab(self.tab_2, "")

        self.suratGosterge = QtWidgets.QGraphicsView(self.tab_2)
        self.suratGosterge.setGeometry(QtCore.QRect(40, 30, 320, 320))
        self.suratGosterge.setObjectName("suratGosterge")
        self.brush = QtGui.QBrush(QtGui.QColor(240, 240, 240))
        self.brush.setStyle(QtCore.Qt.SolidPattern)
        self.suratGosterge.setBackgroundBrush(self.brush)
        self.tabWidget.addTab(self.tab_2, "")
        self.pen = QPen(Qt.yellow)
        self.pen.setWidth(3)
        self.pen.setCapStyle(Qt.RoundCap)
        self.scene = QtWidgets.QGraphicsScene(self.suratGosterge)
        self.pen.setCosmetic(True)
        self.scene.addPixmap(QPixmap('speed2.jpg'))
        self.item = self.scene.addLine(150, 155, 150, 210, self.pen)
        self.pen = QtGui.QPen(QtGui.QColor(QtCore.Qt.gray))
        self.brush = QtGui.QBrush(self.pen.color().darker(100))
        self.scene.addEllipse(133, 132, 35, 35, self.pen, self.brush)
        self.item.setTransformOriginPoint(150, 155)
        self.suratGosterge.setBackgroundBrush(self.brush)
        self.suratGosterge.setScene(self.scene)

        ################################################################################

        self.altimetreGosterge = QtWidgets.QGraphicsView(self.tab_2)
        self.altimetreGosterge.setGeometry(QtCore.QRect(440, 30, 320, 320))
        self.altimetreGosterge.setObjectName("altimetreGosterge")
        self.scene1 = QtWidgets.QGraphicsScene(self.altimetreGosterge)
        self.scene1.addPixmap(QPixmap('altimetre2.jpeg'))
        self.barometrikBasincLabel = QtWidgets.QLabel(self.altimetreGosterge)
        self.barometrikBasincLabel.setGeometry(QtCore.QRect(55, 147, 70, 25))
        self.barometrikBasincLabel.setFont(QFont('Arial Black', 14))
        self.barometrikBasincLabel.setStyleSheet("color: rgb(0,0,0); background-color: rgba(255, 255, 255,0);")
        self.barometrikBasincLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.barometrikBasincLabel.setObjectName("barometrikBasincLabel")
        self.brush1 = QtGui.QBrush(QtGui.QColor(240, 240, 240))
        self.brush1.setStyle(QtCore.Qt.SolidPattern)
        self.pen1 = QPen(Qt.yellow)
        self.pen1.setWidth(5)
        self.pen1.setCapStyle(Qt.RoundCap)
        self.pen1.setCosmetic(True)
        self.item1 = self.scene1.addLine(150, 155, 150, 90, self.pen1)
        self.pen1 = QtGui.QPen(QtGui.QColor(QtCore.Qt.gray))
        self.brush1 = QtGui.QBrush(self.pen1.color().darker(100))
        self.scene1.addEllipse(133, 133, 35, 35, self.pen1, self.brush1)
        self.item1.setTransformOriginPoint(150, 155)
        self.altimetreGosterge.setBackgroundBrush(self.brush1)
        self.altimetreGosterge.setScene(self.scene1)

        ##################################################################################

        self.varyometreGosterge = QtWidgets.QGraphicsView(self.tab_2)
        self.varyometreGosterge.setGeometry(QtCore.QRect(40, 410, 320, 320))
        self.varyometreGosterge.setObjectName("varyometreGosterge")
        self.scene2 = QtWidgets.QGraphicsScene(self.varyometreGosterge)
        self.scene2.addPixmap(QPixmap('varyometre2.jpeg'))
        self.brush2 = QtGui.QBrush(QtGui.QColor(240, 240, 240))
        self.brush2.setStyle(QtCore.Qt.SolidPattern)
        self.pen2 = QPen(Qt.yellow)
        self.pen2.setWidth(8)
        self.pen2.setCapStyle(Qt.RoundCap)
        self.pen2.setCosmetic(True)
        self.item2 = self.scene2.addLine(150, 154, 50, 154, self.pen2)
        self.pen2 = QtGui.QPen(QtGui.QColor(QtCore.Qt.gray))
        self.brush2 = QtGui.QBrush(self.pen2.color().darker(100))
        self.scene2.addEllipse(133, 133, 35, 35, self.pen2, self.brush2)
        self.item2.setTransformOriginPoint(150, 155)
        self.varyometreGosterge.setBackgroundBrush(self.brush2)
        self.varyometreGosterge.setScene(self.scene2)

        ####################################################################################

        self.istikametGyroGosterge = QtWidgets.QGraphicsView(self.tab_2)
        self.istikametGyroGosterge.setGeometry(QtCore.QRect(440, 410, 320, 320))
        self.istikametGyroGosterge.setObjectName("istikametGyroGosterge")
        self.scene3 = QtWidgets.QGraphicsScene(self.istikametGyroGosterge)
        self.scene3.addPixmap(QPixmap('pusula2.jpeg'))
        self.brush3 = QtGui.QBrush(QtGui.QColor(240, 240, 240))
        self.brush3.setStyle(QtCore.Qt.SolidPattern)
        self.pen3 = QPen(Qt.red)
        self.pen3.setWidth(20)
        self.pen3.setCapStyle(Qt.SquareCap)
        self.pen3.setJoinStyle(Qt.MiterJoin)
        self.pen3.setCosmetic(True)
        self.item3 = self.scene3.addLine(150, 155, 150, 90, self.pen3)
        self.pen3 = QtGui.QPen(QtGui.QColor(QtCore.Qt.gray))
        self.item3.setTransformOriginPoint(150, 155)
        self.pen4 = QPen(Qt.white)
        self.pen4.setWidth(20)
        self.pen4.setCapStyle(Qt.SquareCap)
        self.pen4.setJoinStyle(Qt.MiterJoin)
        self.pen4.setCosmetic(True)
        self.item4 = self.scene3.addLine(150, 155, 150, 210, self.pen4)
        self.pen4 = QtGui.QPen(QtGui.QColor(QtCore.Qt.gray))
        self.item4.setTransformOriginPoint(150, 155)
        self.brush3 = QtGui.QBrush(self.pen4.color().darker(100))
        self.istikametGyroGosterge.setBackgroundBrush(self.brush3)
        self.istikametGyroGosterge.setScene(self.scene3)

        ############################################################################################

        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.tab_2)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(910, 10, 911, 741))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.stlgoster = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.stlgoster.setContentsMargins(0, 0, 0, 0)
        self.stlgoster.setObjectName("vertical_2")
        self.gyro()

        ############################################################################################

        self.takimno = QtWidgets.QLabel(self.centralwidget)
        self.takimno.setGeometry(QtCore.QRect(20, 810, 81, 16))
        self.takimno.setStyleSheet("font: 10pt \"Arial Black: bold\";color: #2675a6;")
        self.takimno.setObjectName("label")
        self.paketno = QtWidgets.QLabel(self.centralwidget)
        self.paketno.setGeometry(QtCore.QRect(110, 810, 111, 16))
        self.paketno.setStyleSheet("font: 10pt \"Arial Black: bold\";color: #2675a6;")
        self.paketno.setObjectName("label_14")
        self.saat = QtWidgets.QLabel(self.centralwidget)
        self.saat.setGeometry(QtCore.QRect(230, 810, 151, 16))
        self.saat.setStyleSheet("font: 10pt \"Arial Black: bold\";color: #2675a6;")
        self.saat.setObjectName("label_2")
        self.sicaklik = QtWidgets.QLabel(self.centralwidget)
        self.sicaklik.setGeometry(QtCore.QRect(390, 810, 69, 16))
        self.sicaklik.setStyleSheet("font: 10pt \"Arial Black: bold\";color: #2675a6;")
        self.sicaklik.setObjectName("label_15")
        self.basinc = QtWidgets.QLabel(self.centralwidget)
        self.basinc.setGeometry(QtCore.QRect(475, 810, 91, 16))
        self.basinc.setStyleSheet("font: 10pt \"Arial Black: bold\";color: #2675a6;")
        self.basinc.setObjectName("label_3")
        self.yukseklik = QtWidgets.QLabel(self.centralwidget)
        self.yukseklik.setGeometry(QtCore.QRect(545, 810, 85, 16))
        self.yukseklik.setStyleSheet("font: 10pt \"Arial Black: bold\";color: #2675a6;")
        self.yukseklik.setObjectName("label_17")
        self.inishizi = QtWidgets.QLabel(self.centralwidget)
        self.inishizi.setGeometry(QtCore.QRect(650, 810, 200, 16))
        self.inishizi.setStyleSheet("font: 10pt \"Arial Black: bold\";color: #2675a6;")
        self.inishizi.setObjectName("label_4")
        self.surat = QtWidgets.QLabel(self.centralwidget)
        self.surat.setGeometry(QtCore.QRect(800, 810, 101, 16))
        self.surat.setStyleSheet("font: 10pt \"Arial Black: bold\";color: #2675a6;")
        self.surat.setObjectName("label_16")
        self.yon = QtWidgets.QLabel(self.centralwidget)
        self.yon.setGeometry(QtCore.QRect(890, 810, 51, 16))
        self.yon.setStyleSheet("font: 10pt \"Arial Black: bold\";color: #2675a6;")
        self.yon.setObjectName("label_30")
        self.pilgerilimi = QtWidgets.QLabel(self.centralwidget)
        self.pilgerilimi.setGeometry(QtCore.QRect(950, 810, 131, 16))
        self.pilgerilimi.setStyleSheet("font: 10pt \"Arial Black: bold\";color: #2675a6;")
        self.pilgerilimi.setObjectName("label_5")
        self.latitude = QtWidgets.QLabel(self.centralwidget)
        self.latitude.setGeometry(QtCore.QRect(1070, 810, 130, 16))
        self.latitude.setStyleSheet("font: 10pt \"Arial Black: bold\";color: #2675a6;")
        self.latitude.setObjectName("label_21")
        self.longitude = QtWidgets.QLabel(self.centralwidget)
        self.longitude.setGeometry(QtCore.QRect(1200, 810, 130, 16))
        self.longitude.setStyleSheet("font: 10pt \"Arial Black: bold\";color: #2675a6;")
        self.longitude.setObjectName("label_6")
        self.altitude = QtWidgets.QLabel(self.centralwidget)
        self.altitude.setGeometry(QtCore.QRect(1340, 810, 121, 16))
        self.altitude.setStyleSheet("font: 10pt \"Arial Black: bold\";color: #2675a6;")
        self.altitude.setObjectName("label_18")
        self.pitch = QtWidgets.QLabel(self.centralwidget)
        self.pitch.setGeometry(QtCore.QRect(1470, 810, 51, 16))
        self.pitch.setStyleSheet("font: 10pt \"Arial Black: bold\";color: #2675a6;")
        self.pitch.setObjectName("label_7")
        self.roll = QtWidgets.QLabel(self.centralwidget)
        self.roll.setGeometry(QtCore.QRect(1540, 810, 41, 16))
        self.roll.setStyleSheet("font: 10pt \"Arial Black: bold\";color: #2675a6;")
        self.roll.setObjectName("label_19")
        self.yaw = QtWidgets.QLabel(self.centralwidget)
        self.yaw.setGeometry(QtCore.QRect(1600, 810, 41, 16))
        self.yaw.setStyleSheet("font: 10pt \"Arial Black: bold\";color: #2675a6;")
        self.yaw.setObjectName("label_8")

        self.takimNoText = QtWidgets.QLabel(self.centralwidget)
        self.takimNoText.setGeometry(QtCore.QRect(30, 850, 81, 16))
        self.takimNoText.setStyleSheet("font: 10pt \"Calibri Light: bold\";color: rgb(0, 0, 90);")
        self.takimNoText.setObjectName("takimNoText")
        self.paketSayisiText = QtWidgets.QLabel(self.centralwidget)
        self.paketSayisiText.setGeometry(QtCore.QRect(150, 850, 111, 16))
        self.paketSayisiText.setStyleSheet("font: 10pt \"Calibri Light: bold\";color: rgb(0, 0, 90);")
        self.paketSayisiText.setObjectName("paketSayisiText")
        self.gondermeSaatiText = QtWidgets.QLabel(self.centralwidget)
        self.gondermeSaatiText.setGeometry(QtCore.QRect(240, 850, 151, 16))
        self.gondermeSaatiText.setStyleSheet("font: 10pt \"Calibri Light: bold\";color: rgb(0, 0, 90);")
        self.gondermeSaatiText.setObjectName("gondermeSaatiText")
        self.sicaklikText = QtWidgets.QLabel(self.centralwidget)
        self.sicaklikText.setGeometry(QtCore.QRect(415, 850, 81, 16))
        self.sicaklikText.setStyleSheet("font: 10pt \"Times New Roman\";color: rrgb(0, 0, 90);")
        self.sicaklikText.setObjectName("sicaklikText")
        self.basincText = QtWidgets.QLabel(self.centralwidget)
        self.basincText.setGeometry(QtCore.QRect(495, 850, 61, 16))
        self.basincText.setStyleSheet("font: 10pt \"Times New Roman\";color: rgb(0, 0, 90);")
        self.basincText.setObjectName("basincText")
        self.yukseklikText = QtWidgets.QLabel(self.centralwidget)
        self.yukseklikText.setGeometry(QtCore.QRect(570, 850, 91, 16))
        self.yukseklikText.setStyleSheet("font: 10pt \"Times New Roman\";color: rgb(0, 0, 90);")
        self.yukseklikText.setObjectName("yukseklikText")
        self.inisHiziText = QtWidgets.QLabel(self.centralwidget)
        self.inisHiziText.setGeometry(QtCore.QRect(700, 850, 71, 16))
        self.inisHiziText.setStyleSheet("font: 10pt \"Times New Roman\";color: rgb(0, 0, 90);")
        self.inisHiziText.setObjectName("inisHiziText")
        self.suratText = QtWidgets.QLabel(self.centralwidget)
        self.suratText.setGeometry(QtCore.QRect(815, 850, 121, 16))
        self.suratText.setStyleSheet("font: 10pt \"Times New Roman\";color: rgb(0, 0, 90);")
        self.suratText.setObjectName("suratText")
        self.yonText = QtWidgets.QLabel(self.centralwidget)
        self.yonText.setGeometry(QtCore.QRect(900, 850, 101, 16))
        self.yonText.setStyleSheet("font: 10pt \"Times New Roman\";color: rgb(0, 0, 90);")
        self.yonText.setObjectName("yonText")
        self.pilGerilimiText = QtWidgets.QLabel(self.centralwidget)
        self.pilGerilimiText.setGeometry(QtCore.QRect(990, 850, 101, 16))
        self.pilGerilimiText.setStyleSheet("font: 10pt \"Times New Roman\";color: rgb(0, 0, 90);")
        self.pilGerilimiText.setObjectName("pilGerilimiText")
        self.latitudeText = QtWidgets.QLabel(self.centralwidget)
        self.latitudeText.setGeometry(QtCore.QRect(1100, 850, 121, 16))
        self.latitudeText.setStyleSheet("font: 10pt \"Times New Roman\";color: rgb(0, 0, 90);")
        self.latitudeText.setObjectName("latitudeText")
        self.longitudeText = QtWidgets.QLabel(self.centralwidget)
        self.longitudeText.setGeometry(QtCore.QRect(1240, 850, 131, 16))
        self.longitudeText.setStyleSheet("font: 10pt \"Times New Roman\";color: rgb(0, 0, 90);")
        self.longitudeText.setObjectName("longitudeText")
        self.altitudeText = QtWidgets.QLabel(self.centralwidget)
        self.altitudeText.setGeometry(QtCore.QRect(1375, 850, 111, 16))
        self.altitudeText.setStyleSheet("font: 10pt \"Times New Roman\";color: rgb(0, 0, 90);")
        self.altitudeText.setObjectName("altitudeText")
        self.pitchText = QtWidgets.QLabel(self.centralwidget)
        self.pitchText.setGeometry(QtCore.QRect(1485, 850, 51, 16))
        self.pitchText.setStyleSheet("font: 10pt \"Times New Roman\";color: rgb(0, 0, 90);")
        self.pitchText.setObjectName("pitchText")
        self.rollText = QtWidgets.QLabel(self.centralwidget)
        self.rollText.setGeometry(QtCore.QRect(1555, 850, 41, 16))
        self.rollText.setStyleSheet("font: 10pt \"Times New Roman\";color: rgb(0, 0, 90);")
        self.rollText.setObjectName("rollText")
        self.yawText = QtWidgets.QLabel(self.centralwidget)
        self.yawText.setGeometry(QtCore.QRect(1615, 850, 41, 16))
        self.yawText.setStyleSheet("font: 10pt \"Times New Roman\";color: rgb(0, 0, 90);")
        self.yawText.setObjectName("yawText")

        ########################################################################################################################

        self.graphicsView_5 = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsView_5.setGeometry(QtCore.QRect(1615, 880, 80, 55))
        self.graphicsView_5.setStyleSheet("border-image: url(logo1.png);background: transparent;")
        self.graphicsView_5.setObjectName("graphicsView_5")
        self.graphicsView_6 = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsView_6.setGeometry(QtCore.QRect(1500, 810, 426, 234))
        self.graphicsView_6.setStyleSheet("border-image: url(logo2.png);background: transparent;")
        self.graphicsView_6.setObjectName("graphicsView_6")

        MainWindow.setCentralWidget(self.centralwidget)
        MainWindow.setWindowIcon(QtGui.QIcon("icon.jpg"))
        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def gyro(self):
        self.frame = QFrame()
        self.vl = QVBoxLayout()
        # 1350, 610, 421, 351
        # self.frame.setFixedWidth(410)
        # self.frame.setFixedHeight(351)
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.vl.addWidget(self.vtkWidget)
        self.frame.setLayout(self.vl)
        self.ren = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
        self.reader_zl1 = vtk.vtkSTLReader()
        self.reader_zl1.SetFileName("Final Montaj.STL")
        self.mapper_zl1 = vtk.vtkPolyDataMapper()

        self.transform = vtk.vtkTransform()
        self.transform.RotateX(0)
        self.transform.RotateY(0)
        self.transform.RotateZ(0)
        self.transformFilter = vtk.vtkTransformPolyDataFilter()
        self.transformFilter.SetTransform(self.transform)
        self.transformFilter.SetInputConnection(self.reader_zl1.GetOutputPort())
        self.transformFilter.Update()
        if vtk.VTK_MAJOR_VERSION <= 5:
            self.mapper_zl1.SetInput(self.transformFilter.GetOutput())
        else:
            self.mapper_zl1.SetInputConnection(self.transformFilter.GetOutputPort())
        self.actor_zl1 = vtk.vtkActor()
        self.actor_zl1.SetMapper(self.mapper_zl1)
        self.ren.AddActor(self.actor_zl1)
        self.ren.SetBackground(255 / 255, 255 / 255, 255 / 255)
        self.frame.setLayout(self.stlgoster)
        self.actor_zl1.GetProperty().SetColor(0.5, 0.5, 0.5)  # (R,G,B)
        self.actor_zl1.SetScale(1, 1, 1)
        self.stlgoster.addWidget(self.frame)
        self.onceki1 = 0
        self.onceki2 = 0
        self.iren.Initialize()
        self.iren.Start()

    def baglanClick(self):
        self.my = Thread()
        self.grafikGoster()
        self.haritaCiz()

        csv_writer = csv.writer(open(konum, 'w'), delimiter=',')
        csv_writer.writerow(['TAKIM NO', 'PAKET SAYISI', 'GÖNDERME ZAMANI', 'SICAKLIK', 'BASINÇ', 'YÜKSEKLİK', 'İNİŞ/ÇIKIŞ HIZI', 'SÜRAT', 'YÖN','PİL GERİLİMİ',
                             'GPS LATİTUDE', 'GPS LONGİTUDE', 'GPS ALTİTUDE', 'PİTCH', 'ROLL', 'YAW'])

        self.my.start()

    def grafikGoster(self):
        self.yukseklikGrafik.show()
        self.sicaklikGrafik.show()
        self.basincGrafik.show()
        self.inisHiziGrafik.show()

        if self.grafikZamanlayıcı:
            self.grafikZamanlayıcı.stop()
            self.grafikZamanlayıcı.deleteLater()
            self.grafikZamanlayıcı = None

        self.grafikZamanlayıcı = QtCore.QTimer()
        self.grafikZamanlayıcı.timeout.connect(self.guncelleGrafik)
        self.grafikZamanlayıcı.start(1000)

    def haritaCiz(self):
        self.pointItem = self.view.scene().addCircle(31.7565452, 41.4494227, 5.0) #yarışma alanının konumları girilecek. (longitutde,latitude)
        self.pointItem.setBrush(Qt.blue)
        self.pointItem.setToolTip('10.068640, 44.860767')
        self.pointItem.setFlag(QGraphicsItem.ItemIsSelectable, True)

        if self.grafikZamanlayıcı1:
            self.grafikZamanlayıcı1.stop()
            self.grafikZamanlayıcı1.deleteLater()
            self.grafikZamanlayıcı1 = None

        self.grafikZamanlayıcı1 = QtCore.QTimer()
        self.grafikZamanlayıcı1.timeout.connect(self.guncelleHarita)
        self.grafikZamanlayıcı1.start(1000)

    def guncelleHarita(self):
        self.lats = list()
        self.lons = list()

        # deger, cevir = item nesnesini döndürür. // item : sürat.
        # deger1, cevir1 = item1 nesnesi.         // item1 : altimetre.
        # deger2, cevir2 = item2 nesnesi.         // item2 : varyometre.
        # deger3, cevir3 = item3//4 nesnesi.      // item3 : pusula.


        if len(gpsLongitude) > 0:
            # SÜRAT GÖSTERGE KONTROL
            self.deger = None
            self.deger = int(veri_liste[7])
            if (int(veri_liste[7]) < 6):
                self.cevir = int(self.deger * 4)
            else:
                self.cevir = int(((self.deger * 4) - 4))
            self.item.setRotation(self.cevir)

            #ALTİMETRE GÖSTERGE KONTROL
            self.deger1 = None
            self.deger1 = int(veri_liste[5])
            self.cevir1 = int(self.deger1 * (7))
            self.item1.setRotation(self.cevir1)
            self.barometrikBasincLabel.setText(str(veri_liste[5]))

            #VARYOMETRE GÖSTERGE KONTROL
            self.deger2 = None
            self.deger2 = int(veri_liste[6])
            self.cevir2 = int(self.deger2 * 5)
            self.item2.setRotation(self.cevir2)

            #PUSULA GÖSTERGE KONTROL
            self.deger3 = None
            self.deger3 = int(veri_liste[8])
            self.cevir3 = int(self.deger3)
            self.item3.setRotation(self.cevir3)
            self.item4.setRotation(self.cevir3)

            #HARİTAYA POİNT ATMA. GPS
            self.pointItem = self.view.scene().addCircle(gpsLongitude[0], gpsLatitude[0], 5.0)
            self.pointItem.setBrush(Qt.blue)
            self.pointItem.setPen(QPen(Qt.NoPen))
            self.pointItem.setToolTip('%f, %f' % (gpsLongitude[0], gpsLatitude[0]))
            self.pointItem.setFlag(QGraphicsItem.ItemIsSelectable, True)
            self.lons.append(gpsLongitude[0])
            self.lats.append(gpsLatitude[0])
            # self.polylineItem = self.view.scene().addPolyline(self.lons, self.lats)
            # self.polylineItem.setPen(QPen(QBrush(Qt.red), 3.0))

    def guncelleGrafik(self):
        self.time += 1

        if len(veri_liste) > 0:

            #GRAFİKLERE VERİLERİ ÇEKİP FLOATLA YÖNLENDİRME
            self.yukseklikVeri = float(veri_liste[5])
            self.sicaklikVeri = float(veri_liste[3])
            self.basincVeri = float(veri_liste[4])
            self.inisHiziVeri = float(veri_liste[6])
            self.time_kuyruk.append(self.time)
            self.yukseklikmax.append(self.yukseklikVeri)
            self.sicaklikmax.append(self.sicaklikVeri)
            self.basincmax.append(self.basincVeri)
            self.inisHizimax.append(self.inisHiziVeri)
            time_list = list(self.time_kuyruk)
            yukseklik = list(self.yukseklikmax)
            sicaklik = list(self.sicaklikmax)
            basinc = list(self.basincmax)
            inisHizi = list(self.inisHizimax)

            if self.time > 20:
                self.yukseklikGrafik.setRange(xRange=[self.time - 21, self.time],
                                              yRange=[min(yukseklik[-20:]), max(yukseklik[-20:])])
                self.sicaklikGrafik.setRange(xRange=[self.time - 21, self.time],
                                             yRange=[min(sicaklik[-20:]), max(sicaklik[-20:])])
                self.basincGrafik.setRange(xRange=[self.time - 21, self.time],
                                           yRange=[min(basinc[-20:]), max(basinc[-20:])])
                self.inisHiziGrafik.setRange(xRange=[self.time - 21, self.time],
                                             yRange=[min(inisHizi[-20:]), max(inisHizi[-20:])])

            self.yukseklikG(ad="", x=time_list, y=yukseklik)
            self.sicaklikG(ad="", x=time_list, y=sicaklik)
            self.basincG(ad="", x=time_list, y=basinc)
            self.inisHiziG(ad="", x=time_list, y=inisHizi)


            #PROGRESSBAR SETTİNG
            self.pro = int(veri_liste[9])
            self.progressBar.setValue(self.pro)

            # STL FİLE TRANSFORM
            self.transform.RotateX(self.onceki1 - float(veri_liste[14]))
            self.transform.RotateY(self.onceki2 - float(veri_liste[13]))
            self.transform.RotateZ(0)
            self.vtkWidget.update()
            self.ren.ResetCamera()
            self.onceki1 = float(veri_liste[14])
            self.onceki2 = float(veri_liste[13])

            #VERİ TEXTLERİ
            self.takimNoText.setText(" "+ str(veri_liste[0]))
            self.paketSayisiText.setText(" "+ str(veri_liste[1]))
            self.gondermeSaatiText.setText(" "+ str(veri_liste[2]))
            self.sicaklikText.setText(" " + str(veri_liste[3]) + " C")
            self.basincText.setText(" " + str(veri_liste[4]) + " pa")
            self.yukseklikText.setText(" " + str(veri_liste[5]) + " m")
            self.inisHiziText.setText(" " + str(veri_liste[6]) + " m/s")
            self.suratText.setText(" " + str(veri_liste[7]) + " m/s")
            self.yonText.setText(" "+ str(veri_liste[8]))
            self.pilGerilimiText.setText(" "+ str(veri_liste[9]))
            self.latitudeText.setText(" "+ str(veri_liste[10]))
            self.longitudeText.setText(" "+ str(veri_liste[11]))
            self.altitudeText.setText(" "+ str(veri_liste[12]))
            self.pitchText.setText(" "+ str(veri_liste[13]))
            self.rollText.setText(" "+ str(veri_liste[14]))
            self.yawText.setText(" "+ str(veri_liste[15]))


    #GRAFİK PLOTTİNG
    def yukseklikG(self, ad, x, y):
        if ad in self.cizgi:
            self.cizgi[ad].setData(x, y)
        else:
            self.cizgi[ad] = self.yukseklikGrafik.getPlotItem().plot(pen=pg.mkPen("#9cd9ff", width=3))

    # GRAFİK PLOTTİNG
    def sicaklikG(self, ad, x, y):
        if ad in self.cizgi1:
            self.cizgi1[ad].setData(x, y)
        else:
            self.cizgi1[ad] = self.sicaklikGrafik.getPlotItem().plot(pen=pg.mkPen("#9cd9ff", width=3))

    # GRAFİK PLOTTİNG
    def basincG(self, ad, x, y):
        if ad in self.cizgi2:
            self.cizgi2[ad].setData(x, y)
        else:
            self.cizgi2[ad] = self.basincGrafik.getPlotItem().plot(pen=pg.mkPen("#9cd9ff", width=3))

    # GRAFİK PLOTTİNG
    def inisHiziG(self, ad, x, y):
        if ad in self.cizgi3:
            self.cizgi3[ad].setData(x, y)
        else:
            self.cizgi3[ad] = self.inisHiziGrafik.getPlotItem().plot(pen=pg.mkPen("#9cd9ff", width=3))

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "B-Dispate Yer İstasyonu"))
        self.progressBar.setFormat(_translate("MainWindow", "BATARYA= %p%"))
        self.baglanButon.setText(_translate("MainWindow", "BAĞLAN"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Grafikler / Harita"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Göstergeler"))
        self.takimNoText.setText(_translate("MainWindow", "-"))
        self.paketSayisiText.setText(_translate("MainWindow", "-"))
        self.gondermeSaatiText.setText(_translate("MainWindow", "-"))
        self.sicaklikText.setText(_translate("MainWindow", "-"))
        self.basincText.setText(_translate("MainWindow", "-"))
        self.yukseklikText.setText(_translate("MainWindow", "-"))
        self.inisHiziText.setText(_translate("MainWindow", "-"))
        self.suratText.setText(_translate("MainWindow", "-"))
        self.yonText.setText(_translate("MainWindow", "-"))
        self.pilGerilimiText.setText(_translate("MainWindow", "-"))
        self.latitudeText.setText(_translate("MainWindow", "-"))
        self.longitudeText.setText(_translate("MainWindow", "-"))
        self.altitudeText.setText(_translate("MainWindow", "-"))
        self.pitchText.setText(_translate("MainWindow", "-"))
        self.rollText.setText(_translate("MainWindow", "-"))
        self.yawText.setText(_translate("MainWindow", "-"))

        self.takimno.setText(_translate("MainWindow", "TAKIM NO"))
        self.paketno.setText(_translate("MainWindow", "PAKET SAYISI"))
        self.saat.setText(_translate("MainWindow", "GÖNDERME SAATİ"))
        self.sicaklik.setText(_translate("MainWindow", "SICAKLIK"))
        self.basinc.setText(_translate("MainWindow", "BASINÇ"))
        self.yukseklik.setText(_translate("MainWindow", "YÜKSEKLİK"))
        self.inishizi.setText(_translate("MainWindow", "İNİŞ / ÇIKIŞ HIZI"))
        self.surat.setText(_translate("MainWindow", "SÜRAT"))
        self.yon.setText(_translate("MainWindow", "YÖN"))
        self.pilgerilimi.setText(_translate("MainWindow", "PİL GERİLİMİ"))
        self.latitude.setText(_translate("MainWindow", "GPS LATİTUDE"))
        self.longitude.setText(_translate("MainWindow", "GPS LONGİTUDE"))
        self.altitude.setText(_translate("MainWindow", "GPS ALTİTUDE"))
        self.pitch.setText(_translate("MainWindow", "PITCH"))
        self.roll.setText(_translate("MainWindow", "ROLL"))
        self.yaw.setText(_translate("MainWindow", "YAW"))



class Thread(QThread):
    def __init__(self, parent=None):
        super(Thread, self).__init__(parent)

        seri.baudrate = 9600
        #PORT SEÇİMİ
        seri.port = portName
        seri.open()

    def run(self):
        while True:
            reading = seri.readline()

            if len(str(reading)) > 3:
                z = reading.decode('utf-8')
                t = z.split(':')
                print(z)
                veri_liste.clear()
                veri_liste.append(t[0]) #takım no
                veri_liste.append(t[1]) #paket sayısı
                veri_liste.append(t[2]) #gönderme saati
                veri_liste.append(t[3]) #sıcaklık
                veri_liste.append(t[4]) #basınç
                veri_liste.append(t[5]) #yükseklik
                veri_liste.append(t[6]) #iniş/çıkış hızı (düşey hız)
                veri_liste.append(t[7]) #sürat (yatay hız)
                veri_liste.append(t[8]) #yön (pusuladan alınacak derece verisi)
                veri_liste.append(t[9]) #pil gerilimi
                veri_liste.append(t[10]) #latitude
                veri_liste.append(t[11]) #longitude
                veri_liste.append(t[12]) #altitude
                veri_liste.append(t[13]) #pitch
                veri_liste.append(t[14]) #roll
                veri_liste.append(t[15]) #yaw


                gpsLatitude.clear()
                gpsLongitude.clear()
                gpsLongitude.append(float(t[11]))
                gpsLatitude.append(float(t[10]))

                csv_writer = csv.writer(open(konum, 'a'), delimiter=',')
                csv_writer.writerow([str(t[0]), str(t[1]), str(t[2]), str(t[3]) + " C", str(t[4]) + " pa", str(t[5]) + " m", str(t[6]) + "m/s", str(t[7]) + "m/s", str(t[8]), str(t[9]), str(t[10]),
                                     str(t[11]), str(t[12]),  str(t[13]), str(t[14]), str(t[15])])


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
