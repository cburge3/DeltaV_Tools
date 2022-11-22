def expressionevaluator():
    import sys

    from PyQt5.QtGui import QIcon
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtWidgets import QLineEdit
    from PyQt5.QtWidgets import QMainWindow
    from PyQt5.QtWidgets import QPushButton
    from PyQt5.QtWidgets import QTextBrowser
    from PyQt5.QtWidgets import QVBoxLayout
    from PyQt5.QtWidgets import QWidget



    class Window(QMainWindow):
        def __init__(self):
            super(Window,self).__init__()
            self.setGeometry(50,50,500,300)
            self.setWindowTitle("PyQt Tutorial")
            self.setWindowIcon = QIcon('pyqt_example2.PNG')
            self.home()


        def ExitForm(self):
            sys.exit()

        def home(self):
            vbox = QVBoxLayout()
            textbrowser = QTextBrowser()
            lineedit = QLineEdit()
            btn = QPushButton("QUIT")
            central_widget = QWidget()
            central_widget.setLayout(vbox)
            btn.clicked.connect(self.close)
            vbox.addWidget(textbrowser)
            vbox.addWidget(lineedit)
            vbox.addWidget(btn)
            self.setCentralWidget(central_widget)
            self.show()


    if __name__=="__main__":
        app = QApplication(sys.argv)
        GUI = Window()
        GUI.show()
        sys.exit(app.exec_())
expressionevaluator()