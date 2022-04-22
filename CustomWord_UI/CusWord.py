from Custom_Word_UI import Ui_CustomWord # import UI

import sys
import os
import codecs
from PyQt5 import QtWidgets

class CusWin(QtWidgets.QMainWindow, Ui_CustomWord):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.path = "{}/Software dev/Twtter&News/data_csv/".format(os.getcwd())
        
        self.bt_add.clicked.connect(self.add_func)
        self.show_text()

    def add_func(self):
        text = self.inputWord.text().strip() # get query
        with codecs.open(self.path + 'Custom_Word.txt', 'a+', "utf-8") as f:
            f.write(text+'\n')
        f.close()
        self.inputWord.setText('')
        self.show_text()
    
    def show_text(self):
        with codecs.open(self.path + 'Custom_Word.txt', 'r', "utf-8") as f:
            lines = f.readlines()
        list_text = [e.strip() for e in lines]
        f.close() # ปิดไฟล์
        self.listWidget.clear()
        for i, txt in enumerate(list_text):
            self.listWidget.insertItem(i+1, txt)

def main():
    app = QtWidgets.QApplication(sys.argv)
    main = CusWin()
    main.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()