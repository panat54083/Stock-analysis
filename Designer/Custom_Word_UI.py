# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Custom_Word.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_CustomWord(object):
    def setupUi(self, CustomWord):
        CustomWord.setObjectName("CustomWord")
        CustomWord.resize(290, 464)
        self.centralwidget = QtWidgets.QWidget(CustomWord)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.listWidget = QtWidgets.QListWidget(self.centralwidget)
        self.listWidget.setObjectName("listWidget")
        self.gridLayout.addWidget(self.listWidget, 2, 0, 1, 1)
        self.inputWord = QtWidgets.QLineEdit(self.centralwidget)
        self.inputWord.setObjectName("inputWord")
        self.gridLayout.addWidget(self.inputWord, 0, 0, 1, 1)
        self.bt_add = QtWidgets.QPushButton(self.centralwidget)
        self.bt_add.setObjectName("bt_add")
        self.gridLayout.addWidget(self.bt_add, 0, 2, 1, 1)
        self.bt_del = QtWidgets.QPushButton(self.centralwidget)
        self.bt_del.setObjectName("bt_del")
        self.gridLayout.addWidget(self.bt_del, 1, 2, 1, 1)
        CustomWord.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(CustomWord)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 290, 21))
        self.menubar.setObjectName("menubar")
        CustomWord.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(CustomWord)
        self.statusbar.setObjectName("statusbar")
        CustomWord.setStatusBar(self.statusbar)

        self.retranslateUi(CustomWord)
        QtCore.QMetaObject.connectSlotsByName(CustomWord)

    def retranslateUi(self, CustomWord):
        _translate = QtCore.QCoreApplication.translate
        CustomWord.setWindowTitle(_translate("CustomWord", "Custom Word"))
        self.bt_add.setText(_translate("CustomWord", "Add"))
        self.bt_del.setText(_translate("CustomWord", "Del"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    CustomWord = QtWidgets.QMainWindow()
    ui = Ui_CustomWord()
    ui.setupUi(CustomWord)
    CustomWord.show()
    sys.exit(app.exec_())