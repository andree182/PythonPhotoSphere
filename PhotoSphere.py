import os
import sys

from renderer import Window


fileUrl = ""


def main():
    Window(640, 480).open(fileUrl)


def qtmain():
    from PyQt4 import QtGui, QtCore
    class Example(QtGui.QWidget):

        def __init__(self):
            super(Example, self).__init__()
            self.setWindowFlags(QtCore.Qt.Dialog)

            self.initUI()

        def initUI(self):

            self.btn = QtGui.QPushButton('OK', self)
            self.btn.move(20, 20)
            self.btn.clicked.connect(self.showDialog)

            self.le = QtGui.QLineEdit(self)
            self.le.move(130, 22)

            self.fdBtn = QtGui.QPushButton('Choose', self)
            self.fdBtn.move(280, 20)
            self.fdBtn.clicked.connect(self.chooseFile)

            self.setGeometry(100, 100, 390, 60)
            self.setWindowTitle('Input dialog')
            self.show()

        def chooseFile(self):
            sFileName = QtGui.QFileDialog.getOpenFileName(self, "Open File", "","Files (*.*)" )
            if not sFileName: return
            self.le.setText("file:///"+sFileName)
            self.showDialog()

        def showDialog(self):
            global fileUrl
            text = (str(self.le.text()))
            fileUrl = text
            QtCore.QCoreApplication.instance().quit()

    app = QtGui.QApplication(sys.argv)
    ex = Example()
    ret = app.exec_()
    return ret




if __name__ == '__main__':
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        fileUrl = "file://{0}".format(os.path.abspath(sys.argv[1]))
        main()
        ret = 0
    else:
        ret = qtmain()
        # Your code that must run when the application closes goes here
        main()
    sys.exit(ret)
