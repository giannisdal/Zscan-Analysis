# -*- coding: utf-8 -*-
"""
Created on Wed Aug 25 15:04:54 2021

@author: Dalamaras
"""
import sys
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QPushButton, QVBoxLayout, QLabel, QLineEdit,QFileDialog,QAction, QComboBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5 import QtCore, QtGui, QtWidgets, QtPrintSupport
from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtCore import QFile
import matplotlib.pyplot as plt
from matplotlib import style
import numpy as np
from scipy.integrate import quad
from scipy.optimize import curve_fit
import matplotlib.patches as mpl_patches
import os
import csv, codecs 
from PyQt5.QtGui import QPalette,QColor,QBrush,QLinearGradient
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QHBoxLayout, QApplication, QDialog, QGridLayout, QLayout
from PyQt5.QtWidgets import QApplication, QWidget, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, \
                            QPushButton, QItemDelegate, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import decimal

class FloatDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super().__init__()

    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        editor.setValidator(QDoubleValidator())
        return editor

class TableWidget(QTableWidget):
    def __init__(self, df0):
        super().__init__()
        self.df0 = df0
        nRows, nColumns = self.df0.shape
        self.setColumnCount(nColumns)
        self.setRowCount(nRows)
        self.setHorizontalHeaderLabels(('Energy [μJ]', 'ΔΤp-v',"γ' [μm\N{SUPERSCRIPT TWO}/GW]","β [μm/GW]"))
        self.setItemDelegateForColumn(1, FloatDelegate())

        # data insertion
        for i in range(self.rowCount()):
            for j in range(self.columnCount()):
                self.setItem(i, j, QTableWidgetItem(str(self.df0.iloc[i, j])))

        self.cellChanged[int, int].connect(self.updateDF)   

    def updateDF(self, row, column):
        text = self.item(row, column).text()
        self.df0.iloc[row, column] = text

class Z_scan(QtWidgets.QMainWindow):

    def __init__(self):#, parent=None):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Z scan Analysis")
        self.setFixedSize(1595, 800)
        self.center()
        a=[]
        for i in range(30):
            i=str("")    
            a.append(i)
        self.data0 = {'x': a,'y': a ,"z":a,"w":a}
        self.df0 = pd.DataFrame(self.data0)
        
        # self.p = QPalette()
        # self.gradient = QLinearGradient(0, 3000, 0, 0)
        # self.gradient.setColorAt(1.0, QColor(120, 190, 255))
        # self.gradient.setColorAt(0.0, QColor(20, 13, 70))
        # self.p.setBrush(QPalette.Window, QBrush(self.gradient))
        # self.setPalette(self.p)
        
        #third insert
        self.nameLabel0 = QLabel(self)
        self.nameLabel0.setText('Import Experimental Data: ')
        self.nameLabel0.move(10, 5)
        self.nameLabel0.resize(400, 32)
        #CSV Button
        self.import_csv = QtWidgets.QPushButton('Import Scan', self)
        self.import_csv.clicked.connect(self.getCSV)
        self.import_csv.resize(100,32)
        self.import_csv.move(10, 45)
        self.import_csv.setStyleSheet("border-radius : 50;border : 2px solid grey")
        
        self.topLabel2 = QLabel('Sign:', self)
        self.combobox2 = QComboBox(self)
        self.combobox2.addItem('')
        self.combobox2.addItem('ΔΤp-v > 0')
        self.combobox2.addItem('ΔΤp-v < 0')
        self.v_layout2 = QVBoxLayout()
        self.v_layout2.addWidget(self.topLabel2)
        self.v_layout2.addWidget(self.combobox2)
        self.combobox2.activated[str].connect(self.onSelected_sign)
        self.setLayout(self.v_layout2)
        self.topLabel2.move(270, 45)
        self.topLabel2.resize(150, 32)
        self.combobox2.move(305, 45)
        self.combobox2.resize(100, 32)
        
        self.topLabel3 = QLabel('Aperture:', self)
        self.combobox3 = QComboBox(self)
        self.combobox3.addItem('')
        self.combobox3.addItem('Closed')
        self.combobox3.addItem('Divided')
        self.v_layout3 = QVBoxLayout()
        self.v_layout3.addWidget(self.topLabel3)
        self.v_layout3.addWidget(self.combobox3)
        self.combobox3.activated[str].connect(self.onSelected_Aperture)
        self.setLayout(self.v_layout3)
        self.topLabel3.move(415, 45)
        self.topLabel3.resize(150, 32)
        self.combobox3.move(475, 45)
        self.combobox3.resize(100, 32)
        #First figure
       
        self.figure_initial = plt.figure()#(figsize=(5,5))    
        self.canvas_initial = FigureCanvas(self.figure_initial)
        self.layout_initial_plot = QVBoxLayout()

        self.widget = QtWidgets.QWidget(self)
        self.widget.setLayout(self.layout_initial_plot)
        # self.layout.addWidget(self.toolbar)
        self.layout_initial_plot.addWidget(self.canvas_initial)
        self.layout().addWidget(self.widget)
        self.widget.move(570,0)
        self.widget.resize(600,400)

        #Plot_Initial_Scan Button
        self.plot_initial= QtWidgets.QPushButton('Plot Initial Scan', self)
        self.plot_initial.clicked.connect(self.plot_initial_scan)
        self.plot_initial.resize(130,32)
        self.plot_initial.move(130, 45)
        self.plot_initial.setStyleSheet("border-radius : 50;border : 2px solid black")
        
        #Final figure
        self.figure_final = plt.figure()#figsize=(5,5))    
        self.canvas_final = FigureCanvas(self.figure_final)     
        # self.grid.addWidget(self.canvas_final, 3, 1) 
        self.widget2 = QtWidgets.QWidget(self)
        self.layout_final_plot = QVBoxLayout()
        self.widget2.setLayout(self.layout_final_plot)
        # self.layout.addWidget(self.toolbar)
        self.layout_final_plot.addWidget(self.canvas_final)
        self.layout().addWidget(self.widget2)
        self.widget2.move(960,400)
        self.widget2.resize(600,400)
        
        #Plot_Final_Scan Button
        self.plot_final = QtWidgets.QPushButton('Plot Final Scan', self) 
        self.plot_final.clicked.connect(self.plot_final_scan)
        self.plot_final.resize(100,32)
        self.plot_final.move(470, 280) 
        self.plot_final.setStyleSheet("border-radius : 50;border : 2px solid black")
        #slope figure
        self.figure_slope = plt.figure()#figsize=(5,5))    
        self.canvas_slope = FigureCanvas(self.figure_slope)     
        # self.grid.addWidget(self.canvas_final, 3, 1) 
        self.widget3 = QtWidgets.QWidget(self)
        self.layout_slope = QVBoxLayout()
        self.widget3.setLayout(self.layout_slope)
        # self.layout.addWidget(self.toolbar)
        self.layout_slope.addWidget(self.canvas_slope)
        self.layout().addWidget(self.widget3)
        self.widget3.move(340,400)
        self.widget3.resize(600,400)
        #Plot_Final_Scan Button
        self.plot_final = QtWidgets.QPushButton('Plot Table Values', self) 
        self.plot_final.clicked.connect(self.plot_slopes)
        self.plot_final.resize(155,32)
        self.plot_final.move(160, 758)

        #third insert
        self.nameLabel3 = QLabel(self)
        self.nameLabel3.setText('Insert the Experimental Parameteres: ')
        self.nameLabel3.move(10, 90)
        self.nameLabel3.resize(400, 32)
        
        # self.nameLabel12 = QLabel(self)
        # self.nameLabel12.setText('Δz OA [mm]:')
        # self.nameLabel12.move(245, 90)
        # self.nameLabel12.resize(400, 32)
        # #sixth line
        # self.line12 = QLineEdit(self)  
        # self.line12.move(325, 90)
        # self.line12.resize(50, 32)
        
        # self.nameLabel13 = QLabel(self)
        # self.nameLabel13.setText('Δz CA [mm]:')
        # self.nameLabel13.move(410, 90)
        # self.nameLabel13.resize(400, 32)
        # #sixth line
        # self.line13 = QLineEdit(self)  
        # self.line13.move(490, 90)
        # self.line13.resize(50, 32)
        
        #fourth insert
        self.nameLabel4 = QLabel(self)
        self.nameLabel4.setText('λ [nm]:')
        self.nameLabel4.move(10, 130)
        self.nameLabel4.resize(400, 32)
        #fourth line
        self.line4 = QLineEdit(self)  
        self.line4.move(60, 130)
        self.line4.resize(50, 32)  
        #fifth insert
        self.nameLabel5 = QLabel(self)
        self.nameLabel5.setText('w0 [μm]:')
        self.nameLabel5.move(140, 130)
        self.nameLabel5.resize(400, 32)
        #fifth line
        self.line5 = QLineEdit(self)  
        self.line5.move(200, 130)
        self.line5.resize(50, 32)
        #sixth insert
        self.nameLabel6 = QLabel(self)
        self.nameLabel6.setText('τ [ps]:')
        self.nameLabel6.move(280, 130)
        self.nameLabel6.resize(400, 32)
        #sixth line
        self.line6 = QLineEdit(self)  
        self.line6.move(325, 130)
        self.line6.resize(50, 32)
        #seventh insert
        self.nameLabel7 = QLabel(self)
        self.nameLabel7.setText('Abs:')
        self.nameLabel7.move(25, 180)
        self.nameLabel7.resize(400, 32)
        #seventh line
        self.line7 = QLineEdit(self)  
        self.line7.move(60, 180)
        self.line7.resize(50, 32)
        #eighth insert
        self.nameLabel8 = QLabel(self)
        self.nameLabel8.setText('l [cm]:')
        self.nameLabel8.move(155, 180)
        self.nameLabel8.resize(400, 32)
        #eighth line
        self.line8 = QLineEdit(self)  
        self.line8.move(200, 180)
        self.line8.resize(50, 32)
        #ninth insert
        self.nameLabel9 = QLabel(self)
        self.nameLabel9.setText('E [μJ]:')
        self.nameLabel9.move(285, 180)
        self.nameLabel9.resize(400, 32)
        #ninth line
        self.line9 = QLineEdit(self)  
        self.line9.move(325, 180)
        self.line9.resize(50, 31)
        #first insert
        self.nameLabel1 = QLabel(self)
        self.nameLabel1.setText('CA Focal Point: ')
        self.nameLabel1.move(400, 180)
        self.nameLabel1.resize(150, 32)
        #first line
        self.line1 = QLineEdit(self)  
        self.line1.move(490, 180)
        self.line1.resize(50, 32)      
        
        self.nameLabel15 = QLabel(self)
        self.nameLabel15.setText('OA Focal Point: ')
        self.nameLabel15.move(10, 230)
        self.nameLabel15.resize(100, 32)
        #first line
        self.line15 = QLineEdit(self)  
        self.line15.move(100, 230)
        self.line15.resize(50, 32)  
        
        #second insert
        self.nameLabel2 = QLabel(self)
        self.nameLabel2.setText('OA Baseline :')
        self.nameLabel2.move(170, 230)
        self.nameLabel2.resize(100, 32)
        #second line
        self.line2 = QLineEdit(self)  
        self.line2.move(250, 230)
        self.line2.resize(50, 32)

        #tenth insert
        self.nameLabel10 = QLabel(self)
        self.nameLabel10.setText('CA Baseline:')
        self.nameLabel10.move(330, 230)
        self.nameLabel10.resize(100, 32)
        #tenth line
        self.line10 = QLineEdit(self)  
        self.line10.move(405, 230)
        self.line10.resize(50, 32)
        #eleventh line
        self.nameLabel11 = QLabel(self)
        self.nameLabel11.setText('n\N{SUBSCRIPT ZERO}:')
        self.nameLabel11.move(485, 230)
        self.nameLabel11.resize(100, 32)
        #tenth line
        self.line11 = QLineEdit(self)  
        self.line11.move(505, 230)
        self.line11.resize(50, 32)
        #save
        self.pushButtonWrite = QPushButton('Save Plot as txt ', self)
        self.pushButtonWrite.clicked.connect(self.Savetxt)
        self.pushButtonWrite.resize(130,32)
        self.pushButtonWrite.move(1165, 360)
        self.fileName = ""
        self.fname = ""
        self.model =  QtGui.QStandardItemModel(self)
        self.pushButtonWrite.setStyleSheet("border-radius : 50;border : 2px solid grey")
        
        self.pushButtonWrite2 = QPushButton('Save Table as txt ', self)
        self.pushButtonWrite2.clicked.connect(self.Savetxt_table)
        self.pushButtonWrite2.resize(130,32)
        self.pushButtonWrite2.move(1300, 360)
        self.fileName2 = ""
        self.fname2 = ""
        self.model2 =  QtGui.QStandardItemModel(self)
        self.pushButtonWrite2.setStyleSheet("border-radius : 50;border : 2px solid grey")
        
        self.pushButton3 = QPushButton('Current Intensity', self)
        self.pushButton3.clicked.connect(self.show_text_I0)
        self.pushButton3.resize(150,32)
        self.pushButton3.move(10, 280)
                
        self.show_I0 = QLabel(self)
        self.show_I0.move(170, 280)
        self.show_I0.resize(200, 32)
        
        self.pushButton6 = QPushButton('Absorption Coefficient', self)
        self.pushButton6.clicked.connect(self.show_text_a0)
        self.pushButton6.resize(150,32)
        self.pushButton6.move(10, 320)
                
        self.show_a0 = QLabel(self)
        self.show_a0.move(170, 320)
        self.show_a0.resize(200, 32)
        
        self.pushButton4 = QPushButton('Effective Length', self)
        self.pushButton4.clicked.connect(self.show_text_Leff)
        self.pushButton4.resize(150,32)
        self.pushButton4.move(10, 360)
                
        self.show_Leff = QLabel(self)
        self.show_Leff.move(170, 360)
        self.show_Leff.resize(200, 32)
        
        self.pushButton2 = QPushButton(' NLR parameter', self)
        self.pushButton2.clicked.connect(self.show_text_g)
        self.pushButton2.resize(130,32)
        self.pushButton2.move(1165, 10)
                
        self.show_g = QLabel(self)
        self.show_g.move(1300, 10)
        self.show_g.resize(300, 32)
        
        self.pushButton1 = QPushButton(' NLA coefficient', self)
        self.pushButton1.clicked.connect(self.show_text_b)
        self.pushButton1.resize(130,32)
        self.pushButton1.move(1165, 50)
        
        self.show_beta = QLabel(self)
        self.show_beta.resize(300, 32)
        self.show_beta.move(1300, 50)
        
        self.pushButton7 = QPushButton(' ΔΤp-v', self)
        self.pushButton7.clicked.connect(self.show_text_DTpv)
        self.pushButton7.resize(80,32)
        self.pushButton7.move(400, 360)
                
        self.show_DTpv = QLabel(self)
        self.show_DTpv.move(485, 360)
        self.show_DTpv.resize(80, 50)
        
        self.pushButton13 = QPushButton('T(z=0)', self)
        self.pushButton13.clicked.connect(self.show_text_T0)
        self.pushButton13.resize(80,32)
        self.pushButton13.move(400, 320)
                
        self.show_T0 = QLabel(self)
        self.show_T0.move(485, 320)
        self.show_T0.resize(80, 50)
        
        self.pushButton8 = QPushButton(' Real Part', self)
        self.pushButton8.clicked.connect(self.show_text_g_mean)
        self.pushButton8.resize(130,32)
        self.pushButton8.move(1165, 90)
                
        self.show_g_mean = QLabel(self)
        self.show_g_mean.move(1300, 90)
        self.show_g_mean.resize(300, 32)
        
        self.pushButton9 = QPushButton(' Imaginary Part', self)
        self.pushButton9.clicked.connect(self.show_text_b_mean)
        self.pushButton9.resize(130,32)
        self.pushButton9.move(1165, 130)
                
        self.show_b_mean = QLabel(self)
        self.show_b_mean.move(1300, 130)
        self.show_b_mean.resize(300, 32)
        
        self.pushButton10 = QPushButton(' Susceptibility', self)
        self.pushButton10.clicked.connect(self.show_text_x3)
        self.pushButton10.resize(130,32)
        self.pushButton10.move(1165, 170)
                
        self.show_x3 = QLabel(self)
        self.show_x3.move(1300, 170)
        self.show_x3.resize(300, 32)
        
        self.nameLabel14 = QLabel(self)
        self.nameLabel14.setText('C [mM]:')
        self.nameLabel14.move(1165, 220)
        self.nameLabel14.resize(100, 32)
        #tenth line
        self.line14 = QLineEdit(self)  
        self.line14.move(1215, 220)
        self.line14.resize(50, 32)
        
        self.pushButton11 = QPushButton("Susceptibility/C", self)
        self.pushButton11.clicked.connect(self.show_text_x3_C)
        self.pushButton11.resize(130,32)
        self.pushButton11.move(1165, 260)
                
        self.show_x3_C = QLabel(self)
        self.show_x3_C.move(1300, 260)
        self.show_x3_C.resize(300, 32)
        
        self.pushButton12 = QPushButton('TPA coefficient', self)
        self.pushButton12.clicked.connect(self.show_text_sigma)
        self.pushButton12.resize(130,32)
        self.pushButton12.move(1165, 300)
                
        self.show_sigma = QLabel(self)
        self.show_sigma.move(1330, 300)
        self.show_sigma.resize(300, 32)
        
        self.ok_button_0 = QPushButton('Insert', self)
        # self.ok_button_0.clicked.connect(self.dz_closed)
        # self.ok_button_0.clicked.connect(self.dz_open)
        self.ok_button_0.clicked.connect(self.C)
        self.ok_button_0.clicked.connect(self.n0)
        self.ok_button_0.clicked.connect(self.baseline_closed)
        self.ok_button_0.clicked.connect(self.baseline_open)
        self.ok_button_0.clicked.connect(self.z)
        self.ok_button_0.clicked.connect(self.z_o)
        self.ok_button_0.clicked.connect(self.wavelength)
        self.ok_button_0.clicked.connect(self.beamwaist)
        self.ok_button_0.clicked.connect(self.time)
        self.ok_button_0.clicked.connect(self.Abs)
        self.ok_button_0.clicked.connect(self.length)
        self.ok_button_0.clicked.connect(self.energy)
        self.ok_button_0.resize(60,32)
        self.ok_button_0.move(400, 280)
        self.ok_button_0.setStyleSheet("border-radius : 50;border : 2px solid black")
        
        self.topLabel = QLabel('Pulse Shape:', self)
        self.combobox = QComboBox(self)
        self.combobox.addItem('')
        self.combobox.addItem('Top Hat')
        self.combobox.addItem('Gaussian')
        self.combobox.addItem('sech\N{SUPERSCRIPT TWO}')
        self.v_layout = QVBoxLayout()
        self.v_layout.addWidget(self.topLabel)
        self.v_layout.addWidget(self.combobox)
        self.combobox.activated[str].connect(self.onSelected)
        self.setLayout(self.v_layout)
        self.topLabel.move(410, 130)
        self.topLabel.resize(150, 32)
        self.combobox.move(490, 130)
        self.combobox.resize(80, 32)
        
        self.tableLayout = QVBoxLayout()

        self.table = TableWidget(self.df0)
        
        self.widget4 = QtWidgets.QWidget(self)
        self.widget4.setLayout(self.tableLayout)
        self.tableLayout.addWidget(self.table)
        self.widget4.resize(325,370)
        self.widget4.move(0, 400) 
        
        self.pushButton5 = QPushButton('Insert Table Values', self)
        self.pushButton5.clicked.connect(self.print_DF_Values)
        self.pushButton5.resize(155,32)
        self.pushButton5.move(10, 758)
        self.pushButton5.setStyleSheet("border-radius : 50;border : 2px solid black")
        
        self.show()
        
    def plot_slopes(self):
        self.figure_slope.clear()
        plt.rc('font', weight='bold')
        plt.rcParams["font.family"] = "serif"
        plt.rcParams["mathtext.fontset"] = "dejavuserif"
        self.ax =  self.figure_slope.add_subplot(111)
        self.table_df0["X"]=pd.to_numeric(self.table_df0["x"])
        self.table_df0["Y"]=pd.to_numeric(self.table_df0["y"])
        self.x=pd.DataFrame(self.table_df0['X'])
        self.y=pd.DataFrame(self.table_df0['Y'])
        self.X = self.x.to_numpy()
        self.Y=self.y.to_numpy()
        regression_model = LinearRegression(fit_intercept=False)
        regression_model.fit(self.X, self.Y)
        self.y_predicted = regression_model.predict(self.X)
        rmse = mean_squared_error(self.Y, self.y_predicted)
        r2 = r2_score(self.Y,self.y_predicted)
        print('Slope:' ,regression_model.coef_)
        print('Intercept:', regression_model.intercept_)
        print('Root mean squared error: ', rmse)
        print('R2 score: ', r2)
        self.ax.plot(self.X,self.Y,'o',color="black",markersize=6,label="sample")
        self.ax.plot(np.append(self.X,0), np.append(self.y_predicted,0), color='r',label="")
        self.ax.legend(loc='best')
        if self.sign=="+":
            
            self.ax.set_ylim(bottom=0)
            self.ax.set_xlim(left=0)
        else:
            self.ax.set_ylim(top=0)
            self.ax.set_xlim(left=0)
        self.ax.tick_params(axis='both', direction="in") 
        self.ax.grid(b=None, which='both', axis='both')
        self.ax.set_ylabel("ΔΤp-v",weight='bold')
        self.ax.set_xlabel("Ε [μm]",weight='bold')
        self.slope_linear = ("Slope = "+str("{:.2f}".format(float(regression_model.coef_))))
        print(self.slope_linear)
        
        self.handles = [mpl_patches.Rectangle((0, 0), 1, 1, fc="white", ec="white", 
                                  lw=0, alpha=0)] * 2
        self.labels = []
        self.labels.append(str(self.slope_linear))
        self.ax.legend(self.handles, self.labels, loc='best', fontsize='medium', 
                      fancybox=True, framealpha=0.7, handlelength=0, handletextpad=0)
        self.canvas_slope.draw()

    def plot_final_scan(self):
        plt.rc('font', weight='bold')
        plt.rcParams["font.family"] = "serif"
        plt.rcParams["mathtext.fontset"] = "dejavuserif"
        if self.aperture=="CA":
            self.data["norm_divided"]=self.data["closed"]+1-self.baseline_closed
        elif self.aperture=="D":
            self.data["norm_divided"]=self.data["divided"]+1-self.baseline_closed
        
        self.data["norm_open"]=self.data["open"]+1-self.baseline_open
        self.data["norm_z_closed"]=self.data["z"]-self.z
        self.data["norm_z_open"]=self.data["z"]-self.z_o
        
        # z1_open=int(self.data[self.data["norm_z_open"]==-self.dz_open/2].index.values)
        # z2_open=int(self.data[self.data["norm_z_open"]==self.dz_open/2].index.values)
        # z3_open=int(self.data[self.data["norm_z_open"]==float(self.data['norm_z_open'].values[-1])].index.values)
        
        # z_1_open=np.random.choice([1, 1.01, 0.99,0.98,1.02], p=[0.4, 0.15, 0.15,0.15,0.15], size=(z1_open))
        # z_2_open=np.random.choice([1, 1.01, 0.99,0.98,1.02], p=[0.4, 0.15, 0.15,0.15,0.15], size=(z3_open-z2_open+1))
        
        # self.data["norm_open"]=pd.DataFrame(z_1_open).append(((self.data.loc[
        #     [j for j in range(z1_open,z2_open)],"norm_open_1"]),pd.DataFrame(z_2_open)),ignore_index=True)
        
        self.popt,self.pcov=curve_fit(self.T,self.data["norm_z_open"],self.data["norm_open"],p0=[0.02,1])
        self.perr=np.sqrt(np.diag(self.pcov))
        self.figure_final.clear()
        self.ax =  self.figure_final.add_subplot(111) 
        self.ax.plot(self.data["norm_z_open"],self.data["norm_open"],'o',color="black",markersize=4)
        self.ax.plot(self.data["norm_z_open"],self.T(self.data["norm_z_open"],self.popt[0],self.popt[-1]),color="black")
        self.y=self.T(self.data["norm_z_open"],self.popt[0],self.popt[-1])
        
        # z1_closed=int(self.data[self.data["norm_z_closed"]==-self.dz_open/2].index.values)
        # z2_closed=int(self.data[self.data["norm_z_closed"]==self.dz_open/2].index.values)
        # z3_closed=int(self.data[self.data["norm_z_closed"]==float(self.data['norm_z_closed'].values[-1])].index.values)
        
        # z_1_closed=np.random.choice([1, 1.01, 0.99,0.98,1.02], p=[0.4, 0.15, 0.15,0.15,0.15], size=(z1_closed))
        # z_2_closed=np.random.choice([1, 1.01, 0.99,0.98,1.02], p=[0.4, 0.15, 0.15,0.15,0.15], size=(z3_closed-z2_closed+1))
        
        # self.data["norm_divided"]=pd.DataFrame(z_1_closed).append(((self.data.loc[
        #     [j for j in range(z1_closed,z2_closed)],"norm_divided_1"]),pd.DataFrame(z_2_closed)),ignore_index=True)

        self.poptc,self.pcovc=curve_fit(self.Tc,self.data["norm_z_closed"],self.data["norm_divided"],p0=[0.02,1,1])

        self.perrc=np.sqrt(np.diag(self.pcovc))
        self.ax.plot(self.data["norm_z_closed"],self.data["norm_divided"],'o',color="red",markersize=4)
        self.ax.plot(self.data["norm_z_closed"],self.Tc(self.data["norm_z_closed"],self.poptc[0],self.poptc[1],self.poptc[-1]),color="red")
        self.yo=self.T(self.data["norm_z_open"],self.popt[0],self.popt[-1])
        self.yc=self.Tc(self.data["norm_z_closed"],self.poptc[0],self.poptc[1],self.poptc[-1])
        self.DTpv=max(self.yc)-min(self.yc)
        self.DTpv_value=("ΔΤp-v = " + str("{:.2f}".format(self.DTpv)))
        if self.popt[0]>0:
            self.T0=min(self.yo)
            self.T0_value=("T(z=0) = "+str("{:.2f}".format(self.T0)))
        else:
            self.T0=max(self.yo)
            self.T0_value=("T(z=0) = "+str("{:.2f}".format(self.T0)))

        self.ax.set_ylim(((self.data["norm_open"].min()+self.data["norm_divided"].min())/2)
                         -0.2,((self.data["norm_open"].max()+self.data["norm_divided"].max())/2)+0.2)


        self.ax.legend(loc='best')
        self.ax.tick_params(axis='both', direction="in") 
        self.ax.grid(b=None, which='both', axis='both')
        # self.ax.set_facecolor("wheat")
        self.ax.set_ylabel('Normalized Transmittance ',weight='bold')
        self.ax.set_xlabel('z [mm]',weight='bold')
        
        self.sup5=" "+str(10)+self.get_super("-21")+" m"+self.get_super("2")+"/W"
        self.sup6=" "+str(10)+self.get_super("-15")+" m/W"
        
        self.b=float(self.popt[0])/(self.I1*self.Leff)
        self.b_err=float(self.perr[0])/(self.I1*self.Leff) 
        
        self.beta_value =( "β = "+"("+str("{:.2f}".format(self.b))
                         + u"\u00B1" + str("{:.2f}".format(self.b_err))+")"+str(self.sup6))
        print(self.beta_value)

        self.g=float(self.poptc[0])/(self.k0*self.I2*self.Leff)
        self.g_err=float(self.perrc[0])/(self.k0*self.I2*self.Leff)
        
        self.g_value = ("γ' = "+"("+str("{:.2f}".format(self.g))
                                          + u"\u00B1" + str("{:.2f}".format(self.g_err))+")"+str(self.sup5))
        print(self.g_value)
        
        self.Intensity_value = ("I\N{SUBSCRIPT ZERO} = "+str("{:.2f}".format(self.I0))+' GW/cm\N{SUPERSCRIPT TWO}')
        print(self.Intensity_value)
        
        self.handles = [mpl_patches.Rectangle((0, 0), 1, 1, fc="white", ec="white", 
                                 lw=0, alpha=0)] * 2
        self.labels = []
        self.labels.append(str(self.g_value))
        self.labels.append(str(self.beta_value))
        self.ax.legend(self.handles, self.labels, loc='best', fontsize='medium', 
                      fancybox=True, framealpha=0.7, handlelength=0, handletextpad=0)    
        self.canvas_final.draw()
            
    def plot_initial_scan(self):
        self.figure_initial.clear()
        plt.rc('font', weight='bold')
        plt.rcParams["font.family"] = "serif"
        plt.rcParams["mathtext.fontset"] = "dejavuserif"
        self.ax =  self.figure_initial.add_subplot(111)
        self.ax.plot(self.data["z"],self.data["open"],'-o',color="black",markersize=4, label="Open")
        self.ax.plot(self.data["z"],self.data["closed"],'-o',color="red",markersize=4,label="Closed")
        self.ax.plot(self.data["z"],self.data["divided"],'-o',color="blue",markersize=4,label="Divided")
        self.ax.set_ylim(((self.data["open"].min()+self.data["closed"].min()+self.data["divided"].min())/3)
                         -0.2,((self.data["open"].max()+self.data["closed"].max()+self.data["divided"].max())/3)+0.2)
        self.ax.tick_params(axis='both', direction="in") 
        self.ax.grid(b=None, which='both', axis='both')
        self.ax.set_ylabel('Transmittance ',weight='bold')
        self.ax.set_xlabel('z [mm]',weight='bold')
        self.ax.legend(loc="best")
        self.canvas_initial.draw()
            
    def getCSV(self):
        filePath, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '/home')
        self.data = pd.read_csv(str(filePath), delimiter="\s+") 
        self.data.columns =['z', 'closed',"open","divided"]
        self.data["open"]=self.data["open"]-self.data["open"].mean()+1
        self.data["closed"]=self.data["closed"]-self.data["closed"].mean()+1
        self.data["divided"]=self.data["divided"]-self.data["divided"].mean()+1
        
    def Tc(self,x,g_fit,x0,Q):
        self.I=self.s*self.E/(np.pi*self.w0**2*self.t) #W/m
        self.I0=self.I*10**-13  #GW/cm^2
        self.I2=self.I0*10**-8  #GW/μm^2
        self.a0=(1/self.l)*np.log(10)*self.A   #cm^-1
        n0=str(format(decimal.Decimal(self.a0), '.2e'))
        self.a0_value = ("a\N{SUBSCRIPT ZERO} = "+ self.rewrite(n0) +" cm"+self.get_super("-1"))
        
        n1=str(format(decimal.Decimal(self.Leff*10), '.2e'))        
        self.Leff_value = ("Leff = "+ self.rewrite(n1) +' mm')
        self.Leff=(1-np.exp(-self.a0*self.l))/self.a0    #cm
        self.k0=(10**-2)*2*np.pi/self.L    #L(nm), k0->cm^-1    
        self.z0=np.pi*self.w0**2/self.L*10**3  #mm
        self.x0=x0
        self.g_fit=g_fit
        self.Q=Q
        
        return 1+4*self.g_fit*(x/self.x0)/((1+(x/self.x0)**2)*(9+(x/self.x0)**2)) -2*self.Q*(3+(x/self.x0))/((1+(x/self.x0)**2)*(9+(x/self.x0)**2))

    def T(self,x,b_fit,x0):

        self.I=self.s*self.E/(np.pi*self.w0**2*self.t) #W/m^2
        self.I0=self.I*10**-13  #GW/cm^2
        self.I1=self.I*10**-17  #GW/cm*μm
        self.a0=(1/self.l)*np.log(10)*self.A   #cm^-1
        self.Leff=(1-np.exp(-self.a0*self.l))/self.a0    #mm 
        self.z0=np.pi*self.w0**2/self.L*10**3  #mm
        self.x0=x0
        self.b_fit=b_fit
        
        return  np.log(1+(self.b_fit/(1+x**2/self.x0**2)))/(self.b_fit/(1+x**2/self.x0**2))
    
    # def dz_closed(self):
    #     self.dz_closed=float(self.line13.text()) 
        
    # def dz_open(self):
    #     self.dz_open=float(self.line12.text())    
    #     print(self.dz_open)
    
    def C(self):
        self.C=float(self.line14.text())
    
    def n0(self):
        self.n0=float(self.line11.text())

    def z(self):
        self.z=float(self.line1.text())
        print(str(self.z))
        
    def z_o(self):
        self.z_o=float(self.line15.text())
        print(str(self.z_o))
        
    def baseline_open(self):
        self.baseline_open=float(self.line2.text())
        
    def baseline_closed(self):
        self.baseline_closed=float(self.line10.text())
    
    def wavelength(self):
        self.L=float(self.line4.text())*10**-9
        
    def beamwaist(self):
        self.w0=float(self.line5.text())*10**-6
    
    def time(self):
        self.t=float(self.line6.text())*10**-12
        
    def Abs(self):
        self.A=float(self.line7.text())
 
    def length(self):
        self.l=float(self.line8.text())
        
    def energy(self):
        self.E=float(self.line9.text())*10**-6
        
    def show_text_b(self):
        self.show_beta.setText(str(self.beta_value_mean))
        
    def show_text_g(self):
        self.show_g.setText(str(self.g_value_mean))
        
    def show_text_a0(self):
        self.show_a0.setText(str(self.a0_value))
        
    def show_text_Leff(self):
        self.show_Leff.setText(str(self.Leff_value))
     
    def show_text_I0(self):
        self.show_I0.setText(str(self.Intensity_value))
        
    def show_text_DTpv(self):
        self.show_DTpv.setText(str(self.DTpv_value))
        
    def show_text_T0(self):
        self.show_T0.setText(str(self.T0_value))
        
    def show_text_g_mean(self):
        self.show_g_mean.setText(str(self.Rex_value))
        
    def show_text_b_mean(self):
        self.show_b_mean.setText(str(self.Imx_value))
        
    def show_text_x3(self):
        self.show_x3.setText(str(self.x_value))
        
    def show_text_x3_C(self):
        self.show_x3_C.setText(str(self.x_C_value))
        
    def show_text_sigma(self):
        self.show_sigma.setText(str(self.sigma_value))        
        
    def onSelected(self, txtVal):
        if txtVal=="Top Hat":
            self.s=0.5
        elif txtVal=="Gaussian":
            self.s=2
        elif txtVal=="sech\N{SUPERSCRIPT TWO}":
            self.s=1.76
        else:
            self.s=1
        print(self.s)
        
    def onSelected_Aperture(self, aperture):
        if aperture=="Closed":
            self.aperture="CA"
        elif aperture=="Divided":
            self.aperture="D"         
        else:
            self.aperture=""
        print(self.aperture) 
        
    def onSelected_sign(self, sign):
        if sign=="ΔΤp-v > 0":
            self.sign="+"
        elif sign=="ΔΤp-v < 0":
            self.sign="-"         
        else:
            self.sign=""
        print(self.sign)   
        
    def center(self):
        self.qr = self.frameGeometry()
        self.cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        self.qr.moveCenter(self.cp)
        self.move(self.qr.topLeft())
        
    def Savetxt(self, fileName):        
        name = QFileDialog.getSaveFileName(self, 'Save File', filter='*.txt')
        if(name[0] == ''):
            pass
        else:
            self.data["z_mean"]=(self.data["norm_z_open"]+self.data["norm_z_closed"])/2
            
            self.dictionary={"z": self.data["z_mean"],"OA": self.data["norm_open"],
                             "CA": self.data["norm_divided"] ,
                             "To": self.y,"Tc": self.yc}#,"X":self.X,"Y":self.Y,"predicted":self.y_predicted}  
            self.df = pd.DataFrame(self.dictionary) 
            self.df.to_csv(name[0], index = False)
            
    def Savetxt_table(self, fileName):        
        name = QFileDialog.getSaveFileName(self, 'Save File', filter='*.txt')
        if(name[0] == ''):
            pass
        else:

            self.table_df0.to_csv(name[0], index = False)
            
    def get_super(self,x):
        normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-=()"
        super_s = "ᴬᴮᶜᴰᴱᶠᴳᴴᴵᴶᴷᴸᴹᴺᴼᴾQᴿˢᵀᵁⱽᵂˣʸᶻᵃᵇᶜᵈᵉᶠᵍʰᶦʲᵏˡᵐⁿᵒᵖ۹ʳˢᵗᵘᵛʷˣʸᶻ⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾"
        res = x.maketrans(''.join(normal), ''.join(super_s))
        return x.translate(res)

    def rewrite(self,x):
        n=str(format(decimal.Decimal(x), '.2e'))
        i = int(n[5:7])
        sup=str(10)+self.get_super(str(i))
        j=int(n[0:1])
        m=int(n[2:3])
        r=int(n[3:4])
        cross='\u00D7 '
        return str(j)+"."+str(m)+str(r)+" "+ cross+""+sup
    
    def print_DF_Values(self):
        self.table_df00=self.table.df0
        self.table_df00 = self.table.df0[self.df0.x != str("")]
        self.table_df0= self.table_df00.sort_values('x')
        print(self.table_df0)
        self.table_df0["Re"]=pd.to_numeric(self.table_df0["z"])
        self.table_df0["Im"]=pd.to_numeric(self.table_df0["w"])
        n1_mean=str(format(decimal.Decimal(self.table_df0["Im"].mean()), '.2e'))
        n1_std=str(format(decimal.Decimal(self.table_df0["Im"].std()), '.2e'))
        self.beta_value_mean =( "β = "+"["+"("+self.rewrite(n1_mean)+") "+u"\u00B1" +" ("+ self.rewrite(n1_std)+")"+"] "
                               +str(10)+self.get_super(str(-15))+" m/W")
        
        n2_mean=str(format(decimal.Decimal(self.table_df0["Re"].mean()), '.2e'))
        n2_std=str(format(decimal.Decimal(self.table_df0["Re"].std()), '.2e'))

        self.g_value_mean = ("γ' = "+"["+"("+self.rewrite(n2_mean)+") "+u"\u00B1" +" ("+ self.rewrite(n2_std)+")"+"] "
                             +str(10)+self.get_super(str(-21)) +" m\N{SUPERSCRIPT TWO}/W")
        
        self.Rex=10**-1*10**-6*3*10**10/(480*np.pi**2)*self.n0**2*self.table_df0["Re"].mean()
        self.Rex_std=10**-1*10**-6*3*10**10/(480*np.pi**2)*self.n0**2*self.table_df0["Re"].std()
        
        n3_mean=str(format(decimal.Decimal(self.Rex), '.2e'))
        n3_std=str(format(decimal.Decimal(self.Rex_std), '.2e'))

        # display susceptibilities
        self.sup=str("Reχ"+self.get_super(("(3)"))+" = ")
        self.sup2=" "+str(10)+self.get_super("-16")+" esu"
        
        self.Rex_value = (str(self.sup)+"["+"("+self.rewrite(n3_mean)+") "+ u"\u00B1"+" ("+ self.rewrite(n3_std) +")"+"]"+str(self.sup2))        
        self.Imx=10**21*(10**-7*((3*10**10)**2)*10**-9*10**-9/(2*96*(np.pi**3)*3*10**8))*self.n0**2*self.L*self.table_df0["Im"].mean()
        self.Imx_std=10**21*(10**-7*((3*10**10)**2)*10**-9*10**-9/(2*96*(np.pi**3)*3*10**8))*self.n0**2*self.L*self.table_df0["Im"].std()
        
        n4_mean=str(format(decimal.Decimal(self.Imx), '.2e'))
        n4_std=str(format(decimal.Decimal(self.Imx_std), '.2e'))
        self.sup1=str("Imχ"+self.get_super(("(3)"))+" = ")
        self.Imx_value = (str(self.sup1)+"["+"("+self.rewrite(n4_mean)+") "+ u"\u00B1"+" ("+ self.rewrite(n4_std) +")"+"]"+str(self.sup2)) 
        self.x=np.sqrt(self.Rex**2+self.Imx**2)
        self.x_std=np.sqrt(self.Rex_std**2+self.Imx_std**2)
        self.sup3=str("χ"+self.get_super(("(3)"))+" = ")
        
        n5_mean=str(format(decimal.Decimal(self.x), '.2e'))
        n5_std=str(format(decimal.Decimal(self.x_std), '.2e'))
        self.x_value = (str(self.sup3)+"["+"("+self.rewrite(n5_mean)+") "+ u"\u00B1"+" ("+ self.rewrite(n5_std) +")"+"]"+str(self.sup2)) 
        
        self.x_C=self.x/self.C
        self.x_C_std=self.x_std/self.C
        self.sup4=str("χ"+self.get_super(("(3)"))+"/C") 
        
        n6_mean=str(format(decimal.Decimal(self.x_C), '.2e'))
        n6_std=str(format(decimal.Decimal(self.x_C_std), '.2e'))
        self.x_C_value = (str(self.sup4)+" = "+"[" +"("+self.rewrite(n6_mean)+") "+ u"\u00B1"+" ("+ self.rewrite(n6_std) +")"+"]"+str(self.sup2)+"/mM")       
    
        # h=6.626*10**-
        # self.sigma=
    
def main():
        app = QtWidgets.QApplication(sys.argv)
        w = Z_scan()
        sys.exit(app.exec_())

if __name__ == '__main__':
        main()