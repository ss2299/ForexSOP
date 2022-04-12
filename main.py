from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtGui
from PyQt5 import uic
from Utils.MT5Function import MT5Function
import MetaTrader5 as mt5
import sys
import time
import datetime
import requests
import json
import os

context = dict()
symbols = ["XAUUSD", "XBRUSD", "BTCUSD", "USDJPY"]
timeframes = ["15", "240"]
variables = ["variables"]

form_main = uic.loadUiType("PyQT-Main.ui")[0] #ui 파일 불러오기
# QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

sleepDelay = 5
size = 0.01
SL = 0.0015
TP = 0.0045
cnt_threshold = 7



#쓰레드 선언
class Thread1(QThread):
    sec_changed = pyqtSignal(object)

    

    #parent = MainWidget을 상속 받음.
    def __init__(self, parent=None):
        super().__init__(parent)


    def run(self):
        self.threadRunning = True
        i = 0
        while self.threadRunning:
            try :


                msg = self.readJson()

                self.sec_changed.emit(self.msg)

                time.sleep(sleepDelay)

            except Exception as e:
                print(f"Exception : {e}")


    def readJson(self):
        server_address = "http://192.168.1.122:5000/forex/"
        path = f"{server_address}"
        res = requests.get(path, timeout=120)
        
        if res.status_code == 200:
            self.msg = res.json()
        else:
            print(f"Response Error : {res.status_code}")

class Thread2(QThread):
    sec_changed = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        self.threadRunning = True
        
        while self.threadRunning:
            try :
                self.sec_changed.emit('')

                time.sleep(1)

            except Exception as e:
                print(f"Exception : {e}")



class MainWindow(QMainWindow,QWidget,form_main):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.show()
        self.textBrowser.append(f"[{self.getTime()}] Initialized")

        self.initDict()
        self.initThread()
        self.initTable()

    def closeEvent(self, QCloseEvent):
        re = QMessageBox.question(self, "Confirm", "End this program?",
                    QMessageBox.Yes|QMessageBox.No)

        if re == QMessageBox.Yes:
            self.saveSettings()
            QCloseEvent.accept()
        else:
            QCloseEvent.ignore()  



    def saveSettings(self):
        
        settings = {
            "editLosscut" : self.editLosscut.text(),

            "sbSize_XAUUSD" : self.sbSize_XAUUSD.text(),
            "sbSL_XAUUSD" : self.sbSL_XAUUSD.text(),
            "sbTP_XAUUSD" : self.sbTP_XAUUSD.text(),

            "sbSize_XBRUSD" : self.sbSize_XBRUSD.text(),
            "sbSL_XBRUSD" : self.sbSL_XBRUSD.text(),
            "sbTP_XBRUSD" : self.sbTP_XBRUSD.text(),

            "sbSize_BTCUSD" : self.sbSize_BTCUSD.text(),
            "sbSL_BTCUSD" : self.sbSL_BTCUSD.text(),
            "sbTP_BTCUSD" : self.sbTP_BTCUSD.text(),

            "sbSize_USDJPY" : self.sbSize_USDJPY.text(),
            "sbSL_USDJPY" : self.sbSL_USDJPY.text(),
            "sbTP_USDJPY" : self.sbTP_USDJPY.text(),

            "editLogin" : self.editLogin.text(),
            "editPassword" : self.editPassword.text(),
            "editServer" : self.editServer.text(),
        }

        # Dump json file for interface with Django
        file_path = f"./Settings.json"
        
        with open(file_path, 'w') as outfile:
            json.dump(settings, outfile)

        




        

    def initDict(self):
        self.temp = dict()
        for s in symbols:
            self.temp[s] = dict()
            for t in timeframes:
                self.temp[s][t] = dict()
                for v in variables:
                    self.temp[s][t][v] = dict()
                    
                    self.temp[s][t][v]["obos_upper_cnt"] = 0
                    self.temp[s][t][v]["obos_lower_cnt"] = 0
                    self.temp[s][t][v]["obos_status"] = 0
                    self.temp[s][t][v]["obos_diff"] = 0
                    self.temp[s][t][v]["CCI_upper_cnt"] = 0
                    self.temp[s][t][v]["CCI_lower_cnt"] = 0
                    self.temp[s][t][v]["CCI_status_order"] = 0            # 1 : Up, -1 : Down -> for 1 time order
                    self.temp[s][t][v]["CCI_status_close"] = 0            # 1 : Up, -1 : Down -> for 1 time order
                    self.temp[s][t][v]["CCI_OB_flag"] = False
                    self.temp[s][t][v]["CCI_OS_flag"] = False
                    self.temp[s][t][v]["CCI_OB"] = 100
                    self.temp[s][t][v]["CCI_OS"] = -100                
                    self.temp[s][t][v]["orderBuy_flag"] = False
                    self.temp[s][t][v]["orderSell_flag"] = False
                    self.temp[s][t][v]["closeBuy_flag"] = False
                    self.temp[s][t][v]["closeSell_flag"] = False



    def initUI(self):
        self.setupUi(self)

        self.btnLogin.clicked.connect(self.btnLogin_Cliked) # 버튼 클릭시 연결되는 함수

        # Button Event Connect - XAUUSD
        self.btnBuyXAUUSD.clicked.connect(self.btnBuyXAUUSD_Cliked) # 버튼 클릭시 연결되는 함수
        self.btnSellXAUUSD.clicked.connect(self.btnSellXAUUSD_Cliked) # 버튼 클릭시 연결되는 함수
        self.btnCloseXAUUSD.clicked.connect(self.btnCloseXAUUSD_Cliked) # 버튼 클릭시 연결되는 함수

        # Button Event Connect - XBRUSD
        self.btnBuyXBRUSD.clicked.connect(self.btnBuyXBRUSD_Cliked) # 버튼 클릭시 연결되는 함수
        self.btnSellXBRUSD.clicked.connect(self.btnSellXBRUSD_Cliked) # 버튼 클릭시 연결되는 함수
        self.btnCloseXBRUSD.clicked.connect(self.btnCloseXBRUSD_Cliked) # 버튼 클릭시 연결되는 함수

        # Button Event Connect - BTCUSD
        self.btnBuyBTCUSD.clicked.connect(self.btnBuyBTCUSD_Cliked) # 버튼 클릭시 연결되는 함수
        self.btnSellBTCUSD.clicked.connect(self.btnSellBTCUSD_Cliked) # 버튼 클릭시 연결되는 함수
        self.btnCloseBTCUSD.clicked.connect(self.btnCloseBTCUSD_Cliked) # 버튼 클릭시 연결되는 함수

        # Button Event Connect - USDJPY
        self.btnBuyUSDJPY.clicked.connect(self.btnBuyUSDJPY_Cliked) # 버튼 클릭시 연결되는 함수
        self.btnSellUSDJPY.clicked.connect(self.btnSellUSDJPY_Cliked) # 버튼 클릭시 연결되는 함수
        self.btnCloseUSDJPY.clicked.connect(self.btnCloseUSDJPY_Cliked) # 버튼 클릭시 연결되는 함수

        self.btnBuyXAUUSD.setEnabled(False)
        self.btnSellXAUUSD.setEnabled(False)
        self.btnCloseXAUUSD.setEnabled(False)

        self.btnBuyXBRUSD.setEnabled(False)
        self.btnSellXBRUSD.setEnabled(False)
        self.btnCloseXBRUSD.setEnabled(False)

        self.btnBuyBTCUSD.setEnabled(False)
        self.btnSellBTCUSD.setEnabled(False)
        self.btnCloseBTCUSD.setEnabled(False)

        self.btnBuyUSDJPY.setEnabled(False)
        self.btnSellUSDJPY.setEnabled(False)
        self.btnCloseUSDJPY.setEnabled(False)


        # Initial Value - Spin box
        self.file_path = f"Settings.json"
        if os.path.isfile(self.file_path):
            file_path = f"./Settings.json"
        
            with open(file_path, 'r') as f:
                msg = json.load(f)
            
            self.editLosscut.setText(msg["editLosscut"])

            self.sbSize_XAUUSD.setValue(float(msg["sbSize_XAUUSD"]))
            self.sbSL_XAUUSD.setValue(float(msg["sbSL_XAUUSD"]))
            self.sbTP_XAUUSD.setValue(float(msg["sbTP_XAUUSD"]))

            self.sbSize_XBRUSD.setValue(float(msg["sbSize_XBRUSD"]))
            self.sbSL_XBRUSD.setValue(float(msg["sbSL_XBRUSD"]))
            self.sbTP_XBRUSD.setValue(float(msg["sbTP_XBRUSD"]))

            self.sbSize_BTCUSD.setValue(float(msg["sbSize_BTCUSD"]))
            self.sbSL_BTCUSD.setValue(float(msg["sbSL_BTCUSD"]))
            self.sbTP_BTCUSD.setValue(float(msg["sbTP_BTCUSD"]))

            self.sbSize_USDJPY.setValue(float(msg["sbSize_USDJPY"]))
            self.sbSL_USDJPY.setValue(float(msg["sbSL_USDJPY"]))
            self.sbTP_USDJPY.setValue(float(msg["sbTP_USDJPY"]))

            self.editLogin.setText(msg["editLogin"])
            self.editPassword.setText(msg["editPassword"])
            self.editServer.setText(msg["editServer"])



        else:
            self.sbSize_XAUUSD.setValue(size)
            self.sbSL_XAUUSD.setValue(SL)
            self.sbTP_XAUUSD.setValue(TP)

            self.sbSize_XBRUSD.setValue(0.01)
            self.sbSL_XBRUSD.setValue(0.003)
            self.sbTP_XBRUSD.setValue(0.04)

            self.sbSize_BTCUSD.setValue(0.01)
            self.sbSL_BTCUSD.setValue(0.0025)
            self.sbTP_BTCUSD.setValue(0.0250)

            self.sbSize_USDJPY.setValue(0.01)
            self.sbSL_USDJPY.setValue(0.0006)
            self.sbTP_USDJPY.setValue(0.0060)



    def initThread(self):
        self.th1 = Thread1(self)
        self.th1.sec_changed.connect(self.status_update)

        self.th1.start()

        self.th2 = Thread2(self)
        self.th2.sec_changed.connect(self.account_update)

        self.th2.start()


    def initTable(self):

        # Display currency status
        self.tableStatusXAUUSD = self.tbStatusXAUUSD
        self.tableStatusXAUUSD.setRowCount(6)
        self.tableStatusXAUUSD.setColumnCount(2)

        self.tableStatusXBRUSD = self.tbStatusXBRUSD
        self.tableStatusXBRUSD.setRowCount(6)
        self.tableStatusXBRUSD.setColumnCount(2)

        self.tableStatusBTCUSD = self.tbStatusBTCUSD
        self.tableStatusBTCUSD.setRowCount(6)
        self.tableStatusBTCUSD.setColumnCount(2)

        self.tableStatusUSDJPY = self.tbStatusUSDJPY
        self.tableStatusUSDJPY.setRowCount(6)
        self.tableStatusUSDJPY.setColumnCount(2)

        # QtableWidget 
        self.tableStatusXAUUSD.resizeColumnToContents(1)
        self.tableStatusXAUUSD.resizeRowsToContents()


        # Display account status
        self.tableAccountXAUUSD = self.tbAccountXAUUSD
        self.tableAccountXBRUSD = self.tbAccountXBRUSD
        self.tableAccountBTCUSD = self.tbAccountBTCUSD
        self.tableAccountUSDJPY = self.tbAccountUSDJPY
       

    @pyqtSlot(object)
    def status_update(self, msg):
        self.UI_update(msg)
        self.dictUpdate(msg)
        self.ClosebyCCI(msg)
        self.ClosebyOBOS(msg)
        self.order()
        self.losscut()



    def UI_update(self, msg):
        self.labelTime.setText(msg[symbols[0]][timeframes[0]]["variables"]["date"])

        # XAUUSD
        self.tableStatusXAUUSD.setItem(0, 0, QTableWidgetItem(str(msg[symbols[0]][timeframes[0]]["close"])))
        self.tableStatusXAUUSD.setItem(1, 0, QTableWidgetItem(str(msg[symbols[0]][timeframes[0]]["variables"]["obos_updown"])))
        self.tableStatusXAUUSD.setItem(2, 0, QTableWidgetItem(str(msg[symbols[0]][timeframes[0]]["variables"]["obos_diff"])))
        self.tableStatusXAUUSD.setItem(3, 0, QTableWidgetItem(str(msg[symbols[0]][timeframes[0]]["variables"]["zone_msg"])))
        self.tableStatusXAUUSD.setItem(4, 0, QTableWidgetItem(str(msg[symbols[0]][timeframes[0]]["cci"])))
        self.tableStatusXAUUSD.setItem(5, 0, QTableWidgetItem(str(msg[symbols[0]][timeframes[0]]["ccima"])))

        self.tableStatusXAUUSD.setItem(0, 1, QTableWidgetItem(str(msg[symbols[0]][timeframes[1]]["close"])))
        self.tableStatusXAUUSD.setItem(1, 1, QTableWidgetItem(str(msg[symbols[0]][timeframes[1]]["variables"]["obos_updown"])))
        self.tableStatusXAUUSD.setItem(2, 1, QTableWidgetItem(str(msg[symbols[0]][timeframes[1]]["variables"]["obos_diff"])))
        self.tableStatusXAUUSD.setItem(3, 1, QTableWidgetItem(str(msg[symbols[0]][timeframes[1]]["variables"]["zone_msg"])))
        self.tableStatusXAUUSD.setItem(4, 1, QTableWidgetItem(str(msg[symbols[0]][timeframes[1]]["cci"])))
        self.tableStatusXAUUSD.setItem(5, 1, QTableWidgetItem(str(msg[symbols[0]][timeframes[1]]["ccima"])))


        # XBRUSD
        self.tableStatusXBRUSD.setItem(0, 0, QTableWidgetItem(str(msg[symbols[1]][timeframes[0]]["close"])))
        self.tableStatusXBRUSD.setItem(1, 0, QTableWidgetItem(str(msg[symbols[1]][timeframes[0]]["variables"]["obos_updown"])))
        self.tableStatusXBRUSD.setItem(2, 0, QTableWidgetItem(str(msg[symbols[1]][timeframes[0]]["variables"]["obos_diff"])))
        self.tableStatusXBRUSD.setItem(3, 0, QTableWidgetItem(str(msg[symbols[1]][timeframes[0]]["variables"]["zone_msg"])))
        self.tableStatusXBRUSD.setItem(4, 0, QTableWidgetItem(str(msg[symbols[1]][timeframes[0]]["cci"])))
        self.tableStatusXBRUSD.setItem(5, 0, QTableWidgetItem(str(msg[symbols[1]][timeframes[0]]["ccima"])))

        self.tableStatusXBRUSD.setItem(0, 1, QTableWidgetItem(str(msg[symbols[1]][timeframes[1]]["close"])))
        self.tableStatusXBRUSD.setItem(1, 1, QTableWidgetItem(str(msg[symbols[1]][timeframes[1]]["variables"]["obos_updown"])))
        self.tableStatusXBRUSD.setItem(2, 1, QTableWidgetItem(str(msg[symbols[1]][timeframes[1]]["variables"]["obos_diff"])))
        self.tableStatusXBRUSD.setItem(3, 1, QTableWidgetItem(str(msg[symbols[1]][timeframes[1]]["variables"]["zone_msg"])))
        self.tableStatusXBRUSD.setItem(4, 1, QTableWidgetItem(str(msg[symbols[1]][timeframes[1]]["cci"])))
        self.tableStatusXBRUSD.setItem(5, 1, QTableWidgetItem(str(msg[symbols[1]][timeframes[1]]["ccima"])))


        # BTCUSD
        self.tableStatusBTCUSD.setItem(0, 0, QTableWidgetItem(str(msg[symbols[2]][timeframes[0]]["close"])))
        self.tableStatusBTCUSD.setItem(1, 0, QTableWidgetItem(str(msg[symbols[2]][timeframes[0]]["variables"]["obos_updown"])))
        self.tableStatusBTCUSD.setItem(2, 0, QTableWidgetItem(str(msg[symbols[2]][timeframes[0]]["variables"]["obos_diff"])))
        self.tableStatusBTCUSD.setItem(3, 0, QTableWidgetItem(str(msg[symbols[2]][timeframes[0]]["variables"]["zone_msg"])))
        self.tableStatusBTCUSD.setItem(4, 0, QTableWidgetItem(str(msg[symbols[2]][timeframes[0]]["cci"])))
        self.tableStatusBTCUSD.setItem(5, 0, QTableWidgetItem(str(msg[symbols[2]][timeframes[0]]["ccima"])))

        self.tableStatusBTCUSD.setItem(0, 1, QTableWidgetItem(str(msg[symbols[2]][timeframes[1]]["close"])))
        self.tableStatusBTCUSD.setItem(1, 1, QTableWidgetItem(str(msg[symbols[2]][timeframes[1]]["variables"]["obos_updown"])))
        self.tableStatusBTCUSD.setItem(2, 1, QTableWidgetItem(str(msg[symbols[2]][timeframes[1]]["variables"]["obos_diff"])))
        self.tableStatusBTCUSD.setItem(3, 1, QTableWidgetItem(str(msg[symbols[2]][timeframes[1]]["variables"]["zone_msg"])))
        self.tableStatusBTCUSD.setItem(4, 1, QTableWidgetItem(str(msg[symbols[2]][timeframes[1]]["cci"])))
        self.tableStatusBTCUSD.setItem(5, 1, QTableWidgetItem(str(msg[symbols[2]][timeframes[1]]["ccima"])))


        # USDJPY
        self.tableStatusUSDJPY.setItem(0, 0, QTableWidgetItem(str(msg[symbols[3]][timeframes[0]]["close"])))
        self.tableStatusUSDJPY.setItem(1, 0, QTableWidgetItem(str(msg[symbols[3]][timeframes[0]]["variables"]["obos_updown"])))
        self.tableStatusUSDJPY.setItem(2, 0, QTableWidgetItem(str(msg[symbols[3]][timeframes[0]]["variables"]["obos_diff"])))
        self.tableStatusUSDJPY.setItem(3, 0, QTableWidgetItem(str(msg[symbols[3]][timeframes[0]]["variables"]["zone_msg"])))
        self.tableStatusUSDJPY.setItem(4, 0, QTableWidgetItem(str(msg[symbols[3]][timeframes[0]]["cci"])))
        self.tableStatusUSDJPY.setItem(5, 0, QTableWidgetItem(str(msg[symbols[3]][timeframes[0]]["ccima"])))

        self.tableStatusUSDJPY.setItem(0, 1, QTableWidgetItem(str(msg[symbols[3]][timeframes[1]]["close"])))
        self.tableStatusUSDJPY.setItem(1, 1, QTableWidgetItem(str(msg[symbols[3]][timeframes[1]]["variables"]["obos_updown"])))
        self.tableStatusUSDJPY.setItem(2, 1, QTableWidgetItem(str(msg[symbols[3]][timeframes[1]]["variables"]["obos_diff"])))
        self.tableStatusUSDJPY.setItem(3, 1, QTableWidgetItem(str(msg[symbols[3]][timeframes[1]]["variables"]["zone_msg"])))
        self.tableStatusUSDJPY.setItem(4, 1, QTableWidgetItem(str(msg[symbols[3]][timeframes[1]]["cci"])))
        self.tableStatusUSDJPY.setItem(5, 1, QTableWidgetItem(str(msg[symbols[3]][timeframes[1]]["ccima"])))
        

        self.tableStatusXAUUSD.resizeRowsToContents()
        self.tableStatusXBRUSD.resizeRowsToContents()
        self.tableStatusBTCUSD.resizeRowsToContents()
        self.tableStatusUSDJPY.resizeRowsToContents()

        self.tbAccountXAUUSD.resizeRowsToContents()
        self.tbAccountXBRUSD.resizeRowsToContents()
        self.tbAccountBTCUSD.resizeRowsToContents()
        self.tbAccountUSDJPY.resizeRowsToContents()

        # Closed variable
        self.labelCloseXAUUSD.setText(str(self.temp[symbols[0]][timeframes[0]][variables[0]]["CCI_status_close"]))
        self.labelCloseXBRUSD.setText(str(self.temp[symbols[1]][timeframes[0]][variables[0]]["CCI_status_close"]))
        self.labelCloseBTCUSD.setText(str(self.temp[symbols[2]][timeframes[0]][variables[0]]["CCI_status_close"]))
        self.labelCloseUSDJPY.setText(str(self.temp[symbols[3]][timeframes[0]][variables[0]]["CCI_status_close"]))
        
        # Cell Color
        Color_Warning = QtGui.QColor(255,102,0)
        Color_White = QtGui.QColor(255,255,255)
        Color_Gold = QtGui.QColor(255,215,0)

        if self.temp[symbols[0]][timeframes[0]][variables[0]]["CCI_OB_flag"] == True or msg[symbols[0]][timeframes[0]][variables[0]]["CCI_OS_flag"] == True:
            # if msg[symbols[0]][timeframes[0]]["cci"] > 220 or msg[symbols[0]][timeframes[0]]["cci"] < -220:
            #     self.tableStatusXAUUSD.item(4, 0).setBackground(Color_Gold)
            # else:
            self.tableStatusXAUUSD.item(4, 0).setBackground(Color_Warning)        
        else:
            self.tableStatusXAUUSD.item(4, 0).setBackground(Color_White)

        
        if self.temp[symbols[0]][timeframes[1]][variables[0]]["CCI_OB_flag"] == True or msg[symbols[0]][timeframes[1]][variables[0]]["CCI_OS_flag"] == True:
            # if msg[symbols[0]][timeframes[1]]["cci"] > 220 or msg[symbols[0]][timeframes[1]]["cci"] < -220:
            #     self.tableStatusXAUUSD.item(4, 0).setBackground(Color_Gold)
            # else:
            self.tableStatusXAUUSD.item(4, 1).setBackground(Color_Warning)
        else:
            self.tableStatusXAUUSD.item(4, 1).setBackground(Color_White)

        

        
        if self.temp[symbols[1]][timeframes[0]][variables[0]]["CCI_OB_flag"] == True or self.temp[symbols[1]][timeframes[0]][variables[0]]["CCI_OS_flag"] == True:
            # if msg[symbols[1]][timeframes[0]]["cci"] > 220 or msg[symbols[1]][timeframes[0]]["cci"] < -220:
            #     self.tableStatusXAUUSD.item(4, 0).setBackground(Color_Gold)
            # else:
            self.tableStatusXBRUSD.item(4, 0).setBackground(Color_Warning)
        else:
            self.tableStatusXBRUSD.item(4, 0).setBackground(Color_White)
        
        if self.temp[symbols[1]][timeframes[1]][variables[0]]["CCI_OB_flag"] == True or self.temp[symbols[1]][timeframes[1]][variables[0]]["CCI_OS_flag"] == True:
            # if msg[symbols[1]][timeframes[1]]["cci"] > 220 or msg[symbols[1]][timeframes[1]]["cci"] < -220:
            #     self.tableStatusXAUUSD.item(4, 0).setBackground(Color_Gold)
            # else:
            self.tableStatusXBRUSD.item(4, 1).setBackground(Color_Warning)
        else:
            self.tableStatusXBRUSD.item(4, 1).setBackground(Color_White)

        
        if self.temp[symbols[2]][timeframes[0]][variables[0]]["CCI_OB_flag"] == True or self.temp[symbols[2]][timeframes[0]][variables[0]]["CCI_OS_flag"] == True:
            # if msg[symbols[2]][timeframes[0]]["cci"] > 220 or msg[symbols[2]][timeframes[0]]["cci"] < -220:
            #     self.tableStatusXAUUSD.item(4, 0).setBackground(Color_Gold)
            # else:
            self.tableStatusBTCUSD.item(4, 0).setBackground(Color_Warning)
        else:
            self.tableStatusBTCUSD.item(4, 0).setBackground(Color_White)
        
        if self.temp[symbols[2]][timeframes[1]][variables[0]]["CCI_OB_flag"] == True or self.temp[symbols[2]][timeframes[1]][variables[0]]["CCI_OS_flag"] == True:
            # if msg[symbols[2]][timeframes[1]]["cci"] > 220 or msg[symbols[2]][timeframes[1]]["cci"] < -220:
            #     self.tableStatusXAUUSD.item(4, 0).setBackground(Color_Gold)
            # else:
            self.tableStatusBTCUSD.item(4, 1).setBackground(Color_Warning)
        else:
            self.tableStatusBTCUSD.item(4, 1).setBackground(Color_White)

        

        if self.temp[symbols[3]][timeframes[0]][variables[0]]["CCI_OB_flag"] == True or self.temp[symbols[3]][timeframes[0]][variables[0]]["CCI_OS_flag"] == True:
            # if msg[symbols[3]][timeframes[0]]["cci"] > 220 or msg[symbols[3]][timeframes[0]]["cci"] < -220:
            #     self.tableStatusXAUUSD.item(4, 0).setBackground(Color_Gold)
            # else:
            self.tableStatusUSDJPY.item(4, 0).setBackground(Color_Warning)
        else:
            self.tableStatusUSDJPY.item(4, 0).setBackground(Color_White)
        
        if self.temp[symbols[3]][timeframes[1]][variables[0]]["CCI_OB_flag"] == True or self.temp[symbols[3]][timeframes[1]][variables[0]]["CCI_OS_flag"] == True:
            # if msg[ symbols[3] ][ timeframes[1] ]["cci"] > 220 or msg[ symbols[3 ][ timeframes[1] ]["cci"] < -220:
            #     self.tableStatusXAUUSD.item(4, 0).setBackground(Color_Gold)
            # else:
            self.tableStatusUSDJPY.item(4, 1).setBackground(Color_Warning)
        else:
            self.tableStatusUSDJPY.item(4, 1).setBackground(Color_White)


    def dictUpdate(self, msg):
        for s in symbols:
            for t in timeframes:
                for v in variables:
        
                    if msg[s][t]["cci"] > msg[s][t][v]["CCI_OB"] and msg[s][t]["ccima"] > msg[s][t][v]["CCI_OB"]:    
                        self.temp[s][t][v]["CCI_OB_flag"] = True
                    
                    if msg[s][t]["cci"] < msg[s][t][v]["CCI_OS"] and msg[s][t]["ccima"] < msg[s][t][v]["CCI_OS"]:
                        self.temp[s][t][v]["CCI_OS_flag"] = True
        

    def losscut(self):
        if self.btnBuyXAUUSD.isEnabled():
            positions = self.MT5.positions_get(symbol='')
            for i in positions:
                if not i.type:
                    profit = i.price_current - i.price_open
                else:
                    profit = i.price_open - i.price_current
                
                percentage = profit / i.price_open
                
                if percentage < (float(self.editLosscut.text()) * -1):
                    self.textBrowser.append(f"[{self.getTime()}] {i.symbol}, {i.volume} {self.editLosscut.text()} Loss Cut")
                    self.MT5.closePositionTicket(symbol=i.symbol, ticket=i.ticket)


                    
            

        

        

    
    def ClosebyCCI(self, msg):
        
        for s in symbols:
            for t in timeframes:
                for v in variables:
                    if t == timeframes[0]:
                        if msg[s][t][v]["CCI_lower_cnt"] > 0 and self.temp[s][t][v]["CCI_status_close"] != 1:

                            # CCI Cross CCIMA
                            if self.cbCloseCCIMA_XAUUSD.isChecked() and s == symbols[0]:
                                self.temp[s][t][v]["CCI_status_close"] = 1
                                self.textBrowser.append(f"[{self.getTime()}] {s}, {t} CCI cross CCIMA -> Close Buy")
                                self.temp[s][t][v]["closeBuy_flag"] = True

                            if self.cbCloseCCIMA_XBRUSD.isChecked() and s == symbols[1]:
                                self.temp[s][t][v]["CCI_status_close"] = 1
                                self.textBrowser.append(f"[{self.getTime()}] {s}, {t} CCI cross CCIMA -> Close Buy")
                                self.temp[s][t][v]["closeBuy_flag"] = True

                            if self.cbCloseCCIMA_BTCUSD.isChecked() and s == symbols[2]:
                                self.temp[s][t][v]["CCI_status_close"] = 1
                                self.textBrowser.append(f"[{self.getTime()}] {s}, {t} CCI cross CCIMA -> Close Buy")
                                self.temp[s][t][v]["closeBuy_flag"] = True

                            if self.cbCloseCCIMA_USDJPY.isChecked() and s == symbols[3]:
                                self.temp[s][t][v]["CCI_status_close"] = 1
                                self.textBrowser.append(f"[{self.getTime()}] {s}, {t} CCI cross CCIMA -> Close Buy")
                                self.temp[s][t][v]["closeBuy_flag"] = True

                            

                        if msg[s][t][v]["CCI_upper_cnt"] > 0 and self.temp[s][t][v]["CCI_status_close"] != -1:
                            if self.cbCloseCCIMA_XAUUSD.isChecked() and s == symbols[0]:
                                self.temp[s][t][v]["CCI_status_close"] = -1
                                self.textBrowser.append(f"[{self.getTime()}] {s}, {t} CCI cross CCIMA -> Close Sell")
                                self.temp[s][t][v]["closeSell_flag"] = True
                            
                            if self.cbCloseCCIMA_XBRUSD.isChecked() and s == symbols[1]:
                                self.temp[s][t][v]["CCI_status_close"] = -1
                                self.textBrowser.append(f"[{self.getTime()}] {s}, {t} CCI cross CCIMA -> Close Sell")
                                self.temp[s][t][v]["closeSell_flag"] = True
                            
                            if self.cbCloseCCIMA_BTCUSD.isChecked() and s == symbols[2]:
                                self.temp[s][t][v]["CCI_status_close"] = -1
                                self.textBrowser.append(f"[{self.getTime()}] {s}, {t} CCI cross CCIMA -> Close Sell")
                                self.temp[s][t][v]["closeSell_flag"] = True
                            
                            if self.cbCloseCCIMA_USDJPY.isChecked() and s == symbols[3]:
                                self.temp[s][t][v]["CCI_status_close"] = -1
                                self.textBrowser.append(f"[{self.getTime()}] {s}, {t} CCI cross CCIMA -> Close Sell")
                                self.temp[s][t][v]["closeSell_flag"] = True

                        if self.temp[s][t][v]["CCI_OB_flag"] == True and msg[s][t]["cci"] < msg[s][t][v]["CCI_OB"] and msg[s][t]["ccima"] < msg[s][t][v]["CCI_OB"]:
                            if self.cbCloseCCI_XAUUSD.isChecked() and s == symbols[0]:
                                self.temp[s][t][v]["CCI_OB_flag"] = False
                                self.temp[s][t][v]["closeBuy_flag"] = True
                                self.textBrowser.append(f"[{self.getTime()}] {s}, {t} CCI, CCIMA cross 100 -> Close Buy")

                            if self.cbCloseCCI_XBRUSD.isChecked() and s == symbols[1]:
                                self.temp[s][t][v]["CCI_OB_flag"] = False
                                self.temp[s][t][v]["closeBuy_flag"] = True
                                self.textBrowser.append(f"[{self.getTime()}] {s}, {t} CCI, CCIMA cross 100 -> Close Buy")

                            if self.cbCloseCCI_BTCUSD.isChecked() and s == symbols[2]:
                                self.temp[s][t][v]["CCI_OB_flag"] = False
                                self.temp[s][t][v]["closeBuy_flag"] = True
                                self.textBrowser.append(f"[{self.getTime()}] {s}, {t} CCI, CCIMA cross 100 -> Close Buy")

                            if self.cbCloseCCI_USDJPY.isChecked() and s == symbols[3]:
                                self.temp[s][t][v]["CCI_OB_flag"] = False
                                self.temp[s][t][v]["closeBuy_flag"] = True
                                self.textBrowser.append(f"[{self.getTime()}] {s}, {t} CCI, CCIMA cross 100 -> Close Buy")
                            

                        if self.temp[s][t][v]["CCI_OS_flag"] == True and msg[s][t]["cci"] > msg[s][t][v]["CCI_OS"] and msg[s][t]["ccima"] > msg[s][t][v]["CCI_OS"]:
                            if self.cbCloseCCI_XAUUSD.isChecked() and s == symbols[0]:
                                self.temp[s][t][v]["CCI_OS_flag"] = False
                                self.temp[s][t][v]["closeSell_flag"] = True
                                self.textBrowser.append(f"[{self.getTime()}] {s}, {t} CCI,CCIMA cross -100 -> Close Sell")

                            if self.cbCloseCCI_XBRUSD.isChecked() and s == symbols[1]:
                                self.temp[s][t][v]["CCI_OS_flag"] = False
                                self.temp[s][t][v]["closeSell_flag"] = True
                                self.textBrowser.append(f"[{self.getTime()}] {s}, {t} CCI,CCIMA cross -100 -> Close Sell")

                            if self.cbCloseCCI_BTCUSD.isChecked() and s == symbols[2]:
                                self.temp[s][t][v]["CCI_OS_flag"] = False
                                self.temp[s][t][v]["closeSell_flag"] = True
                                self.textBrowser.append(f"[{self.getTime()}] {s}, {t} CCI,CCIMA cross -100 -> Close Sell")

                            if self.cbCloseCCI_USDJPY.isChecked() and s == symbols[3]:
                                self.temp[s][t][v]["CCI_OS_flag"] = False
                                self.temp[s][t][v]["closeSell_flag"] = True
                                self.textBrowser.append(f"[{self.getTime()}] {s}, {t} CCI,CCIMA cross -100 -> Close Sell")

                            
    def ClosebyOBOS(self, msg):
        for s in symbols:
            for t in timeframes:
                for v in variables:

                    ## OBOS BUY
                    if msg[s][t][v]["obos_upper_cnt"] > cnt_threshold and self.temp[s][t][v]["obos_status"] != 1:

                        # Filtering program was restarted
                        if self.temp[s][t][v]["obos_status"] == 0:
                            self.temp[s][t][v]["obos_status"] = 1
                            continue

                        elif self.temp[s][t][v]["obos_status"] == -1:
                            self.temp[s][t][v]["obos_status"] = 1

                            if t == timeframes[0]:                                  # When 15min OBOS UP is happened
                                self.temp[s][t][v]["closeSell_flag"] = True
                                self.textBrowser.append(f"[{self.getTime()}] {s}, {t} OBOS BUY -> Close Sell")
                                                 
                    # OBOS SELL
                    if msg[s][t][v]["obos_lower_cnt"] > cnt_threshold and self.temp[s][t][v]["obos_status"] != -1:
                        
                        # Filtering program was restarted
                        if self.temp[s][t][v]["obos_status"] == 0:
                            self.temp[s][t][v]["obos_status"] = -1
                            continue

                        elif self.temp[s][t][v]["obos_status"] == 1:
                            self.temp[s][t][v]["obos_status"] = -1
                            
                            if t == timeframes[0]:                                  # When 15min OBOS DOWN is happened
                                self.temp[s][t][v]["closeBuy_flag"] = True
                                self.textBrowser.append(f"[{self.getTime()}] {s}, {t} OBOS SELL -> Close Buy")



    def order(self):
        if self.btnBuyXAUUSD.isEnabled():
            
            for s in symbols:
                for t in timeframes:
                    for v in variables:
                        if self.temp[s][t][v]["closeBuy_flag"] == True:
                            
                            if len(self.MT5.positions_get(symbol=s)) > 0:
                                self.MT5.closePosition(symbol=s, position="buy")
                                self.textBrowser.append(f"[{self.getTime()}] {s}, {t} Close Buy")
                            self.temp[s][t][v]["closeBuy_flag"] = False


                        if self.temp[s][t][v]["closeSell_flag"] == True:
                            
                            if len(self.MT5.positions_get(symbol=s)) > 0:
                                self.MT5.closePosition(symbol=s, position="sell")
                                self.textBrowser.append(f"[{self.getTime()}] {s}, {t} Close Sell")
                            self.temp[s][t][v]["closeSell_flag"] = False


                            


    @pyqtSlot(object)
    def account_update(self, msg):

        # XAUUSD

        sum_buy_volume_XAUUSD = 0
        sum_buy_profit_XAUUSD = 0
        sum_sell_volume_XAUUSD = 0
        sum_sell_profit_XAUUSD = 0       
    
        if self.btnBuyXAUUSD.isEnabled():
            positions = self.MT5.positions_get(symbols[0])

            if len(positions) > 0:
                for i in range(len(positions)):
                    if positions[i].type == 0:          # Buy
                        sum_buy_volume_XAUUSD += positions[i].volume
                        sum_buy_profit_XAUUSD += positions[i].profit
                        
                    elif positions[i].type == 1:        # Sell
                        sum_sell_volume_XAUUSD += positions[i].volume
                        sum_sell_profit_XAUUSD += positions[i].profit

        self.tableAccountXAUUSD.setItem(0, 0, QTableWidgetItem(str( round(sum_buy_volume_XAUUSD,2) )))
        self.tableAccountXAUUSD.setItem(0, 1, QTableWidgetItem(str( round(sum_buy_profit_XAUUSD,2) )))
        self.tableAccountXAUUSD.setItem(1, 0, QTableWidgetItem(str( round(sum_sell_volume_XAUUSD,2) )))
        self.tableAccountXAUUSD.setItem(1, 1, QTableWidgetItem(str( round(sum_sell_profit_XAUUSD,2) )))

        self.tableAccountXAUUSD.resizeRowsToContents()


        # XBRUSD
        sum_buy_volume_XBRUSD = 0
        sum_buy_profit_XBRUSD = 0
        sum_sell_volume_XBRUSD = 0
        sum_sell_profit_XBRUSD = 0       
    
        if self.btnBuyXBRUSD.isEnabled():
            positions = self.MT5.positions_get(symbols[1])

            if len(positions) > 0:
                for i in range(len(positions)):
                    if positions[i].type == 0:          # Buy
                        sum_buy_volume_XBRUSD += positions[i].volume
                        sum_buy_profit_XBRUSD += positions[i].profit
                        
                    elif positions[i].type == 1:        # Sell
                        sum_sell_volume_XBRUSD += positions[i].volume
                        sum_sell_profit_XBRUSD += positions[i].profit

        self.tableAccountXBRUSD.setItem(0, 0, QTableWidgetItem(str( round(sum_buy_volume_XBRUSD,2) )))
        self.tableAccountXBRUSD.setItem(0, 1, QTableWidgetItem(str( round(sum_buy_profit_XBRUSD,2) )))
        self.tableAccountXBRUSD.setItem(1, 0, QTableWidgetItem(str( round(sum_sell_volume_XBRUSD,2) )))
        self.tableAccountXBRUSD.setItem(1, 1, QTableWidgetItem(str( round(sum_sell_profit_XBRUSD,2) )))

        self.tableAccountXBRUSD.resizeRowsToContents()


        # BTCUSD

        sum_buy_volume_BTCUSD = 0
        sum_buy_profit_BTCUSD = 0
        sum_sell_volume_BTCUSD = 0
        sum_sell_profit_BTCUSD = 0       
    
        if self.btnBuyBTCUSD.isEnabled():
            positions = self.MT5.positions_get(symbols[2])

            if len(positions) > 0:
                for i in range(len(positions)):
                    if positions[i].type == 0:          # Buy
                        sum_buy_volume_BTCUSD += positions[i].volume
                        sum_buy_profit_BTCUSD += positions[i].profit
                        
                    elif positions[i].type == 1:        # Sell
                        sum_sell_volume_BTCUSD += positions[i].volume
                        sum_sell_profit_BTCUSD += positions[i].profit

        self.tableAccountBTCUSD.setItem(0, 0, QTableWidgetItem(str( round(sum_buy_volume_BTCUSD,2) )))
        self.tableAccountBTCUSD.setItem(0, 1, QTableWidgetItem(str( round(sum_buy_profit_BTCUSD,2) )))
        self.tableAccountBTCUSD.setItem(1, 0, QTableWidgetItem(str( round(sum_sell_volume_BTCUSD,2) )))
        self.tableAccountBTCUSD.setItem(1, 1, QTableWidgetItem(str( round(sum_sell_profit_BTCUSD,2) )))

        self.tableAccountBTCUSD.resizeRowsToContents()


        # USDJPY

        sum_buy_volume_USDJPY = 0
        sum_buy_profit_USDJPY = 0
        sum_sell_volume_USDJPY = 0
        sum_sell_profit_USDJPY = 0       
    
        if self.btnBuyUSDJPY.isEnabled():
            positions = self.MT5.positions_get(symbols[3])

            if len(positions) > 0:
                for i in range(len(positions)):
                    if positions[i].type == 0:          # Buy
                        sum_buy_volume_USDJPY += positions[i].volume
                        sum_buy_profit_USDJPY += positions[i].profit
                        
                    elif positions[i].type == 1:        # Sell
                        sum_sell_volume_USDJPY += positions[i].volume
                        sum_sell_profit_USDJPY += positions[i].profit

        self.tableAccountUSDJPY.setItem(0, 0, QTableWidgetItem(str( round(sum_buy_volume_USDJPY,2) )))
        self.tableAccountUSDJPY.setItem(0, 1, QTableWidgetItem(str( round(sum_buy_profit_USDJPY,2) )))
        self.tableAccountUSDJPY.setItem(1, 0, QTableWidgetItem(str( round(sum_sell_volume_USDJPY,2) )))
        self.tableAccountUSDJPY.setItem(1, 1, QTableWidgetItem(str( round(sum_sell_profit_USDJPY,2) )))

        self.tableAccountUSDJPY.resizeRowsToContents()



        # Trade Account
        if self.btnBuyXAUUSD.isEnabled():
            account = self.MT5.account_info()
            self.editBalance.setText(str(account.balance))
            self.editEquity.setText(str(account.equity))
            self.editMargin.setText(str(account.margin))
            self.editFreemargin.setText(str(account.margin_free))
            
        

            

        
        

    def btnLogin_Cliked(self): #pushButton 클릭되었을때 구현되는 함수
        
        self.MT5 = MT5Function(int(self.editLogin.text()))
    
        result = self.MT5.connect(account=int(self.editLogin.text()), password=self.editPassword.text(), server=self.editServer.text())

        if result:
            self.textBrowser.append(f"[{self.getTime()}] Login Success")
            
            self.btnBuyXAUUSD.setEnabled(True)
            self.btnSellXAUUSD.setEnabled(True)
            self.btnCloseXAUUSD.setEnabled(True)

            self.btnBuyXBRUSD.setEnabled(True)
            self.btnSellXBRUSD.setEnabled(True)
            self.btnCloseXBRUSD.setEnabled(True)

            self.btnBuyBTCUSD.setEnabled(True)
            self.btnSellBTCUSD.setEnabled(True)
            self.btnCloseBTCUSD.setEnabled(True)

            self.btnBuyUSDJPY.setEnabled(True)
            self.btnSellUSDJPY.setEnabled(True)
            self.btnCloseUSDJPY.setEnabled(True)
            
        else:
            self.textBrowser.append(f"[{self.getTime()}] Login Failed")

    ###    
    ### Button Event - XAUUSD
    ###
    def btnBuyXAUUSD_Cliked(self): #pushButton 클릭되었을때 구현되는 함수
        
        result = self.MT5.order(symbol=symbols[0], buysell="buy", volume=float(self.sbSize_XAUUSD.text()), slpercent=float(self.sbSL_XAUUSD.text()), tppercent=float(self.sbTP_XAUUSD.text()),comment="Manual", magic=1001)
        self.orderReturn(result=result, msg=f"{symbols[0]} Buy")
        self.temp[symbols[0]][timeframes[0]][variables[0]]["CCI_status_close"] = -1
        self.temp[symbols[0]][timeframes[1]][variables[0]]["CCI_status_close"] = -1
        

    
    def btnSellXAUUSD_Cliked(self): #pushButton 클릭되었을때 구현되는 함수
        
        result = self.MT5.order(symbol=symbols[0], buysell="sell", volume=float(self.sbSize_XAUUSD.text()), slpercent=float(self.sbSL_XAUUSD.text()), tppercent=float(self.sbTP_XAUUSD.text()),comment="Manual", magic=1002)
        self.orderReturn(result=result, msg=f"{symbols[0]} Sell")
        self.temp[symbols[0]][timeframes[0]][variables[0]]["CCI_status_close"] = 1
        self.temp[symbols[0]][timeframes[1]][variables[0]]["CCI_status_close"] = 1

    
    def btnCloseXAUUSD_Cliked(self): #pushButton 클릭되었을때 구현되는 함수
        
        self.MT5.closePosition(symbol=symbols[0], position="buysell")

        self.textBrowser.append(f"[{self.getTime()}] {symbols[0]} Position is(are) closed")

    
    ###    
    ### Button Event - XBRUSD
    ###
    def btnBuyXBRUSD_Cliked(self): #pushButton 클릭되었을때 구현되는 함수
        
        result = self.MT5.order(symbol=symbols[1], buysell="buy", volume=float(self.sbSize_XBRUSD.text()), slpercent=float(self.sbSL_XBRUSD.text()), tppercent=float(self.sbTP_XBRUSD.text()),comment="Manual", magic=1001)
        self.orderReturn(result=result, msg=f"{symbols[1]} Buy")
        self.temp[symbols[1]][timeframes[0]][variables[0]]["CCI_status_close"] = -1
        self.temp[symbols[1]][timeframes[1]][variables[0]]["CCI_status_close"] = -1
        

    
    def btnSellXBRUSD_Cliked(self): #pushButton 클릭되었을때 구현되는 함수

        result = self.MT5.order(symbol=symbols[1], buysell="sell", volume=float(self.sbSize_XBRUSD.text()), slpercent=float(self.sbSL_XBRUSD.text()), tppercent=float(self.sbTP_XBRUSD.text()),comment="Manual", magic=1002)
        self.orderReturn(result=result, msg=f"{symbols[1]} Sell")
        self.temp[symbols[1]][timeframes[0]][variables[0]]["CCI_status_close"] = 1
        self.temp[symbols[1]][timeframes[1]][variables[0]]["CCI_status_close"] = 1

    
    def btnCloseXBRUSD_Cliked(self): #pushButton 클릭되었을때 구현되는 함수

        self.MT5.closePosition(symbol=symbols[1], position="buysell")
        self.textBrowser.append(f"[{self.getTime()}] {symbols[1]} Position is(are) closed")

    

    ###    
    ### Button Event - BTCUSD
    ###
    def btnBuyBTCUSD_Cliked(self): #pushButton 클릭되었을때 구현되는 함수

        # if float(self.tableStatusBTCUSD.item(4, 0).text()) > 100:
        #     msgBox = QMessageBox()
        #     msgBox.setIcon(QMessageBox.Information)
        #     msgBox.setText("CCI value is higher than 100. \nDo You really want to buy?")
        #     msgBox.setWindowTitle("CCI")
        #     msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        #     returnValue = msgBox.exec()
        #     if returnValue == QMessageBox.Ok:
        #         print('OK clicked')


        result = self.MT5.order(symbol=symbols[2], buysell="buy", volume=float(self.sbSize_BTCUSD.text()), slpercent=float(self.sbSL_BTCUSD.text()), tppercent=float(self.sbTP_BTCUSD.text()),comment="Manual", magic=1001)
        self.orderReturn(result=result, msg=f"{symbols[2]} Buy")
        self.temp[symbols[2]][timeframes[0]][variables[0]]["CCI_status_close"] = -1
        self.temp[symbols[2]][timeframes[1]][variables[0]]["CCI_status_close"] = -1
        

    
    def btnSellBTCUSD_Cliked(self): #pushButton 클릭되었을때 구현되는 함수

        # if float(self.tableStatusBTCUSD.item(4, 0).text()) < -100:
        #     msgBox = QMessageBox()
        #     msgBox.setIcon(QMessageBox.Information)
        #     msgBox.setText("CCI value is lower than -100. \nDo You really want to sell?")
        #     msgBox.setWindowTitle("CCI")
        #     msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        #     returnValue = msgBox.exec()

        # if returnValue == QMessageBox.Ok:
        result = self.MT5.order(symbol=symbols[2], buysell="sell", volume=float(self.sbSize_BTCUSD.text()), slpercent=float(self.sbSL_BTCUSD.text()), tppercent=float(self.sbTP_BTCUSD.text()),comment="Manual", magic=1002)
        self.orderReturn(result=result, msg=f"{symbols[2]} Sell")
        self.temp[symbols[2]][timeframes[0]][variables[0]]["CCI_status_close"] = 1
        self.temp[symbols[2]][timeframes[1]][variables[0]]["CCI_status_close"] = 1

    
    def btnCloseBTCUSD_Cliked(self): #pushButton 클릭되었을때 구현되는 함수

        self.MT5.closePosition(symbol=symbols[2], position="buysell")
        self.textBrowser.append(f"[{self.getTime()}] {symbols[2]} Position is(are) closed")



    ###    
    ### Button Event - USDJPY
    ###
    def btnBuyUSDJPY_Cliked(self): #pushButton 클릭되었을때 구현되는 함수

        result = self.MT5.order(symbol=symbols[3], buysell="buy", volume=float(self.sbSize_USDJPY.text()), slpercent=float(self.sbSL_USDJPY.text()), tppercent=float(self.sbTP_USDJPY.text()),comment="Manual", magic=1001)
        self.orderReturn(result=result, msg=f"{symbols[3]} Buy")
        self.temp[symbols[3]][timeframes[0]][variables[0]]["CCI_status_close"] = -1
        self.temp[symbols[3]][timeframes[1]][variables[0]]["CCI_status_close"] = -1

    
    def btnSellUSDJPY_Cliked(self): #pushButton 클릭되었을때 구현되는 함수

        result = self.MT5.order(symbol=symbols[3], buysell="sell", volume=float(self.sbSize_USDJPY.text()), slpercent=float(self.sbSL_USDJPY.text()), tppercent=float(self.sbTP_USDJPY.text()),comment="Manual", magic=1002)
        self.orderReturn(result=result, msg=f"{symbols[3]} Sell")
        self.temp[symbols[3]][timeframes[0]][variables[0]]["CCI_status_close"] = 1
        self.temp[symbols[3]][timeframes[1]][variables[0]]["CCI_status_close"] = 1
    
    def btnCloseUSDJPY_Cliked(self): #pushButton 클릭되었을때 구현되는 함수

        self.MT5.closePosition(symbol=symbols[3], position="buysell")
        self.textBrowser.append(f"[{self.getTime()}] {symbols[3]} Position is(are) closed")



    def orderReturn(self, result, msg):
        if result.retcode != 10009:
            self.textBrowser.append(f"[{self.getTime()}] {msg} Order Failed , Comment = {result.comment}")
        if result.retcode == 10009:
            self.textBrowser.append(f"[{self.getTime()}] {msg} Order Success , Volume = {result.volume}, Price = {result.price}")


    def getTime(self):
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return now


    


        

        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    sys.exit(app.exec_())